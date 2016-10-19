#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import bson
from bson.objectid import ObjectId
from flask import render_template, request, Response, stream_with_context, jsonify, g, redirect, url_for
from app import mongo
from . import historyApp
from ..diff import svncheck
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.lexers.diff import DiffLexer
from pygments.formatters import HtmlFormatter

ConfigParser = None


@historyApp.route('/')
def index():
    return "Index"


# 목록 조회, 추가
@historyApp.route('/history', methods=['GET', 'POST'])
def historyListView():
    # db.tblBranch.insert({"url": "/trunk/gui", "srev": 77035, "lrev": 77035, "product": "MF2"})
    global ConfigParser
    if ConfigParser is None:
        import ConfigParser
    config = ConfigParser.ConfigParser();
    config.read('config.ini')
    svnurl = config.get('svn', 'MF2.url')

    returnCode = 200;
    if request.method == 'POST':
        mongo.db.tblBranch.insert_one({'url': request.form.get('url', ''), 'frev': request.form.get('frev', ''),
                                       'trev': request.form.get('frev', ''),
                                       'product': request.form.get('product', 'MF2'), 'count': 0, 'lastdate': ''})
        return redirect(url_for('.historyListView'))
    else:
        lists = mongo.db.tblBranch.find()
        return render_template('history/historyListView.html', data=lists, svnurl=svnurl), returnCode


# 한개 조회,수정,삭제
@historyApp.route('/history/<string:id>', methods=['GET', 'PUT', 'DELETE'])
def historyView(id):
    if request.method == 'GET':
        global ConfigParser
    if ConfigParser is None:
        import ConfigParser
    config = ConfigParser.ConfigParser();
    # SVN 설정 정보 로딩
    config.read('config.ini')
    pSvnId = request.args.get('svnid', '')
    pFlag = request.args.get('flag', '')
    pOffset = int(request.args.get('offset', 0))
    if pOffset < 0:
        pOffset = 0

    result = mongo.db.tblBranch.find_one({"_id": ObjectId(id)})
    print result
    # path_info = g.db.execute('select * from svn_info where s_path_id=?', [pSID]).fetchall()

    svnrooturl = ''
    if result['product'] == 'MF2' or result['product'] == 'AE':
        svnrooturl = config.get('svn', result['product'] + '.url')
        svnurl = svnrooturl + result['url']
    else:
        svnrooturl = config.get('svn', result['product'] + '.url')
        svnurl = svnrooturl + result['url']

    s = svncheck(svnrooturl, result['url'], '', '', config.get('svn', 'uid'), config.get('svn', 'upass'))

    # 마지막 리비전 조회
    last_revision = s.getLastRevision()

    resultlist = []

    print int(result['trev']), last_revision
    # DB에 저장된 최종 리비전이 리파지토리 최종 리비전 보다 작을 경우 변경 로그 조회
    if int(result['trev']) < last_revision:
        # cur = g.db.cursor()
        # cur.execute('update svn_info set s_last_revision=? where s_path_url=?', [last_revision, path_info[0][1]])
        log = s.diffrence(int(result['trev']) + 1, last_revision)
        tmpUpdateRevision = result['trev']
        for info in log:
            print info
            tmpUpdateRevision = info.revision.number
            result = mongo.db.tblHistory.insert_one({'tblBranchKey': ObjectId(id), 'revision': info.revision.number,
                                                     'svnid': info.author,
                                                     'date': time.ctime(info.date),
                                                     'comment': info.message.decode('utf8'), 'paths': []})
            pathlist = []
            for pathinfo in info.changed_paths:
                difftext = None
                # 파일 수정
                if pathinfo.action == 'M':
                    # 인코딩 에러가 발생할 경우 빈값으로 셋팅
                    try:
                        difftext = s.getDiffText(info.revision.number, pathinfo.path).decode('utf-8')
                    except:
                        difftext = ''
                # 파일 추가
                elif pathinfo.action == 'A':
                    # 인코딩 에러가 발생할 경우 빈값으로 셋팅
                    try:
                        difftext = pathinfo.action + ' ' + s.getText(info.revision.number, pathinfo.path).decode(
                            'utf-8')
                    except:
                        difftext = ''
                # 파일 삭제
                elif pathinfo.action == 'D':
                    difftext = pathinfo.action + ' ' + pathinfo.path

                if difftext:
                    difftext = highlight(difftext.decode("utf-8"), DiffLexer(), HtmlFormatter())

                tmpPath = pathinfo.path.decode('utf-8')
                mongo.db.tblHistory.update_one({'_id': ObjectId(result.inserted_id)}, {
                    '$push': {'paths': {'action': pathinfo.action, 'file': tmpPath, 'diff': difftext}}})

        result = mongo.db.tblBranch.find_one_and_update({"_id": ObjectId(id)}, {"$set": {"trev": last_revision}})

    if pFlag == 'n':
        pOffset += 10
    elif pFlag == 'p':
        pOffset -= 10
    else:
        pOffset = 0

    print pSvnId

    if pSvnId:
        result = mongo.db.tblHistory.find({'tblBranchKey': ObjectId(id), "svnid": {'$regex': pSvnId}}).skip(
            pOffset).limit(10)
    else:
        result = mongo.db.tblHistory.find({'tblBranchKey': ObjectId(id)}).skip(pOffset).limit(10)

    param = {'svnurl': svnurl, 'sid': id, 'offset': pOffset}

    return render_template('history/historyView.html', data=result, param=param)


@historyApp.route('/history/del/<string:id>', methods=['GET'])
def historyDel(id):
    result = mongo.db.tblBranch.delete_one({"_id": ObjectId(id)})
    print result.deleted_count, id
    return redirect(url_for('.historyListView'))
