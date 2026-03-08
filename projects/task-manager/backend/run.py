from app import create_app
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)