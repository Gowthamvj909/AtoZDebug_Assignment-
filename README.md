# AtoZDebug_Assignment-

Setup Instructions:
	Clone the Repository:
		git clone <repository-url>
		cd library_management

	Set Up Virtual Environment:
		python -m venv venv
		source venv/bin/activate  # On Windows: venv\Scripts\activate

	Install Dependencies:
		pip install -r requirements.txt
		Environment Variables:

	Create a .env file in the core directory with the following:
		SECRET_KEY=your_secret_key
		MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/<database>
		UPLOAD_DIR=uploads/

	Set Up MongoDB:
		Create collections: users and books.
		Seed initial users with roles ("Admin", "Member").

	Run the Application:
		uvicorn main:app --reload

	Access the Application:
		Open your browser at: http://localhost:8000
