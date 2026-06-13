class Messages:

    # COMMON
    SUCCESS = "Success"
    FAILURE = "Failure"
    ERROR = "Error"

    # INTERNAL ERROR
    INTERNAL_SERVER_ERROR = "Internal server error"

    # GENERAL FAILURE
    VALIDATION_FAILED = "Validation failed"
    DATA_NOT_FOUND = "Data not found"
    INVALID_SORT_FIELD = "Invalid sort field"

    # AUTH
    INVALID_CREDENTIALS = "Invalid username or password"
    ACCESS_DENIED = "You don't have permission to access this resource"
    INVALID_OR_EXPIRED_TOKEN = "Token is missing, invalid, or expired"
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logout successful"
    AUTHENTICATION_FAILED = "Authentication failed"

    # USER
    USER_NOT_FOUND = "User not found"
    USER_CREATED = "User created successfully"
    USER_ALREADY_PRESENT = "User already present"
    USER_DELETED_PERMANENTLY = "User permanently deleted successfully"
    USER_DELETED = "User deleted successfully"
    USERS_FETCHED = "User(s) fetched successfully"
    USER_DETAILS_FETCHED = "User details fetched successfully"
    USER_ACCOUNT_DEACTIVATED = "User details fetched successfully"
    USER_INACTIVE = "User account is inactive"
    USER_NOT_FOUND_OR_INACTIVE = "User not found or inactive"
    USER_SELF_DELETE_NOT_ALLOWED = "Self account deletion is not allowed"
    SUPERADMIN_DELETE_NOT_ALLOWED = "SuperAdmin account cannot be deleted"
    USER_DEACTIVATION_REQUIRED = "Deactivate the user before permanent deletion"

    # PRODUCT
    PRODUCT_ADDED = "Product added successfully"
    PRODUCT_ALREADY_EXISTS = "Product already exists with same SKU"
    PRODUCTS_FETCHED = "Product(s) fetched successfully"
    NO_PRODUCTS_FOUND = "No products found"
    PRODUCT_DETAILS_FETCHED = "Product details fetched successfully"
    PRODUCT_NOT_FOUND = "Product not found"
    PRODUCT_UPDATED = "Product updated successfully"
    PRODUCT_DELETED = "Product deleted successfully"
    PRODUCT_DELETED_PERMANENTLY = "Product permanently deleted successfully"
    PRODUCT_PERMANENT_DELETE_NOT_ALLOWED = "Admin cannot permanently delete products"
    PRODUCT_DEACTIVATION_REQUIRED = "Deactivate the product before permanent deletion"
    INVALID_SKU = "Invalid SKU format"
    PRODUCT_INACTIVE = "Product is inactive"

    # PURCHASES
    PURCHASE_CREATED = "Purchase created successfully"
    PURCHASE_NOT_FOUND = "Purchase not found"
    PURCHASES_FETCHED = "Purchases fetched successfully"
    NO_PURCHASES_FOUND = "No purchases found"
    INVALID_PURCHASE_ID = "Invalid purchase Id"
