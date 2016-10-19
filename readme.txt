mongod --dbpath "D:\Programs\MongoDB\Data"


tblBranch
- url : string
- frev : int
- trev : int
- product : string

tblHistory
- tblBranchKey : int
- revision : int
- svnid : string
- date : date
- comment : string
- paths : document
    - action
    - file : string
    - diff : string




tblBranch

{"url": "/trunk/gui", "srev": 77035, "lrev": 77035, "product": "MF2"}