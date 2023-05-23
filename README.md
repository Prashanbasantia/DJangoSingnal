# Step 1:
### Start Server Python manage.py runserver
# Step 2:
    import the POSTMAN_COLLECTION.json FILE in POSTMAN (FOR API TEST)
# Step 3:
    ## API Uses
    1. Signup api (successfully: two cookies store in postman Seasionid , CSRFtoken)
    2. Posts API 
        * In POST & PUT method's header add value of CSRFToken in key "X-CSRFToken"
    
