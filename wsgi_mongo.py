from app import *

import sys
reload(sys)
sys.setdefaultencoding('UTF8')

application = create_app()
application.config.from_object({"DEBUG":"True","SECRET_KEY":"hellogit00"})

if __name__ == "__main__":
    application.run()