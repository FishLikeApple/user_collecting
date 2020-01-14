from environment import *
import user_collecting

if __name__ == '__main__':

    app.secret_key = "real_secret_key"
    app.debug = False
    app.run(host='0.0.0.0', port=80)
