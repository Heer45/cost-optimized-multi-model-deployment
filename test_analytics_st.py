from streamlit.testing.v1 import AppTest

def test_analytics():
    at = AppTest.from_file("app.py")
    
    # Run the app
    at.run()
    
    # Switch to Cost Analytics page
    at.sidebar.radio[0].set_value("Cost Analytics")
    at.run()
    
    # Check for exceptions
    if at.exception:
        print("EXCEPTION ENCOUNTERED:", at.exception)
    else:
        print("SUCCESS! Page rendered without errors.")

if __name__ == "__main__":
    test_analytics()
