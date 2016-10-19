from app import *

import sys
reload(sys)
sys.setdefaultencoding('UTF8')

application = create_app()
application.config.from_json('../memo_setting.json')

if __name__ == "__main__":
    application.run()