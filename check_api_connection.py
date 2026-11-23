
from api_client import check_api_connection

result = check_api_connection()

print("=" * 50)
print("FASTAPI CONNECTION TEST")
print("=" * 50)

print(result)

if "error" not in result:
    print("\nSUCCESS: Streamlit can communicate with FastAPI!")
else:
    print("\nFAILED: Check whether FastAPI is running.")
