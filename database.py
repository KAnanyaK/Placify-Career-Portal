import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime
import streamlit as st

load_dotenv()

class MongoDB:
    def __init__(self):
        self.connected = False
        try:
            self.connection_string = os.getenv("MONGODB_URI")
            self.database_name = os.getenv("DATABASE_NAME", "placement_portal")
            
            # Connect to MongoDB Atlas
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            
            # Test connection
            self.client.admin.command('ping')
            print(f"✅ MongoDB Atlas connected to {self.database_name}")
            
            # Initialize collections (tables)
            self.students = self.db.students
            self.drives = self.db.drives  
            self.drives_collection = self.db["drives"] 
            self.applications = self.db.applications
            self.applications_collection = self.db["applications"]

            self.create_indexes()
            self.connected = True
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.connected = False
    
    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Student table indexes
            self.students.create_index("student_id", unique=True)
            self.students.create_index("email_id", unique=True)
            self.students.create_index("roll_number", unique=True, sparse=True)
            
            # Drive table indexes  
            self.drives.create_index("company_id", unique=True)
            self.drives.create_index("deadline")
            
            # Application table indexes
            self.applications.create_index("app_id", unique=True)
            self.applications.create_index([("student_id", 1), ("company_id", 1)], unique=True)
            
            print("✅ Database indexes created")
        except Exception as e:
            print(f"⚠️ Index warning: {e}")
    
    # STUDENT OPERATIONS (When student clicks "Save Profile")
    def create_student(self, student_data):
        """Create new student record in database"""
        if not self.connected:
            return {"success": True, "student_id": "demo_123", "message": "Demo mode"}
            
        try:
            # Auto-generate student_id
            last_student = self.students.find_one(sort=[("student_id", -1)])
            student_data['student_id'] = (last_student['student_id'] + 1) if last_student else 10001
            
            # Add timestamps
            student_data['created_at'] = datetime.now()
            student_data['updated_at'] = datetime.now()
            
            # Insert into MongoDB
            result = self.students.insert_one(student_data)
            print(f"✅ Student created: {student_data['student_name']} (ID: {student_data['student_id']})")
            
            return {"success": True, "student_id": student_data['student_id']}
            
        except pymongo.errors.DuplicateKeyError as e:
            if "email_id" in str(e):
                return {"success": False, "message": "Email already exists"}
            elif "roll_number" in str(e):
                return {"success": False, "message": "Roll number already exists"}
            return {"success": False, "message": "Student already exists"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_student_by_email(self, email):
        """Get student data from database"""
        if not self.connected:
            return None
        try:
            return self.students.find_one({"email_id": email})
        except Exception as e:
            print(f"❌ Error getting student: {e}")
            return None
    
    def update_student(self, student_id, update_data):
        """Update student record in database"""
        if not self.connected:
            return {"success": True, "modified_count": 1, "message": "Demo mode"}
            
        try:
            update_data['updated_at'] = datetime.now()
            result = self.students.update_one(
                {"student_id": student_id},
                {"$set": update_data}
            )
            print(f"✅ Student {student_id} updated")
            return {"success": True, "modified_count": result.modified_count}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    # DRIVE OPERATIONS (When admin creates drives)
    def create_drive(self, drive_data):
    #"""Create new placement drive"""
        if not self.connected:
            return {"success": True, "company_id": "demo_1001"}

        try:
            # Auto-generate company_id with prefix 'D'
            last_drive = self.drives_collection.find_one(
                {"company_id": {"$regex": "^D"}}, 
                sort=[("company_id", -1)]
            )
            if last_drive:
                # Extract numeric suffix, e.g. "D105" -> 105
                num = int(last_drive["company_id"][1:]) + 1
            else:
                num = 101
            new_id = f"D{num}"
            drive_data["company_id"] = new_id
            drive_data["created_at"] = datetime.now()

            result = self.drives_collection.insert_one(drive_data)
            print(f"✅ Drive created: {drive_data['company_name']} with ID {new_id}")
            return {"success": True, "company_id": new_id}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def get_all_drives(self):
        """Get all placement drives"""
        if not self.connected:
            return []
        try:
            return list(self.drives.find().sort("deadline", 1))
        except Exception as e:
            return []
    
    def get_eligible_drives(self, student_cgpa):
    #Return drives where CGPA cutoff <= student's CGPA and deadline has not passed"""
        if not self.connected:
            return []
        try:
            from datetime import datetime
            now = datetime.now()
            return list(self.drives.find({
                "cutoff": {"$lte": student_cgpa},
                "deadline": {"$gte": now}
            }).sort("deadline", 1))
        except Exception as e:
            print(f"❌ Error in get_eligible_drives: {e}")
            return []

    def get_student_applications(self, student_id):
    #Return all application documents for a given student_id"""
        if not self.connected:
            return []
        try:
            return list(self.applications.find({"student_id": student_id}).sort("apply_date", -1))
        except Exception as e:
            print(f"❌ Error in get_student_applications: {e}")
            return []

    def get_all_applications(self):
    #Return all application documents for a given student_id"""
        if not self.connected:
            return []
        try:
            return list(self.applications.find().sort("apply_date", -1))
        except Exception as e:
            print(f"❌ Error in get_all_applications: {e}")
            return []
    
    def update_drive(self, company_id, update_data):
    #"""Update a placement drive by company_id"""
        try:
            result = self.drives_collection.update_one(
                {"company_id": company_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                return {"success": True, "message": "Drive updated successfully"}
            else:
                return {"success": False, "message": "Drive not found or no changes made"}
        except Exception as e:
            return {"success": False, "message": f"Error updating drive: {str(e)}"}

    def delete_drive(self, company_id):
    #"""Delete a placement drive by company_id"""
        try:
            result = self.drives_collection.delete_one({"company_id": company_id})
            if result.deleted_count > 0:
                return {"success": True, "message": "Drive deleted successfully"}
            else:
                return {"success": False, "message": "Drive not found"}
        except Exception as e:
            return {"success": False, "message": f"Error deleting drive: {str(e)}"}
    
    # APPLICATION OPERATIONS (When student applies)
    def create_application(self, application_data):
        """Create new application with string ID and set status/date."""
        if not self.connected:
            return {"success": True, "app_id": "demo_5001"}

        try:
            # Find last application with ID starting with 'A'
            last_app = self.applications_collection.find_one(
                {"app_id": {"$regex": "^A"}},
                sort=[("app_id", -1)]
            )

            if last_app and last_app.get("app_id", "").startswith("A"):
                # Extract numeric suffix (e.g. "A201" -> 201) and increment
                num = int(last_app["app_id"][1:]) + 1
            else:
                num = 5001

            new_id = f"A{num}"
            application_data["app_id"]     = new_id
            application_data["apply_date"] = datetime.now()
            application_data["status"]     = "Applied"

            self.applications_collection.insert_one(application_data)
            print(f"✅ Application created: {new_id}")
            return {"success": True, "app_id": new_id}

        except pymongo.errors.DuplicateKeyError:
            return {"success": False, "message": "Already applied to this company"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    
    def update_application_status(self, app_id: str, new_status: str):
    #"""Update the status field of an application by app_id."""
        try:
            result = self.applications_collection.update_one(
                {"app_id": app_id},
                {"$set": {"status": new_status}}
            )
            if result.modified_count > 0:
                return {"success": True, "message": "Application status updated"}
            else:
                return {"success": False, "message": "Application not found or status unchanged"}
        except Exception as e:
            return {"success": False, "message": f"Error updating application status: {e}"}

    def test_connection(self):
        return self.connected
