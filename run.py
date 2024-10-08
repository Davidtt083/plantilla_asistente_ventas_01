import os
from _init_ import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 4000)))