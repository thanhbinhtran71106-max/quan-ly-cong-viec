from app import create_app

app = create_app()

# Vercel Serverless Function entry point
if __name__ == '__main__':
    app.run(debug=True)
