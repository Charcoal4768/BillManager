export function fetch_token(type) {
    if (type == "admin") {
        fetch('/api/request_admin_token', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(tokenData => {
            if (tokenData.publish_token) {
                return tokenData.publish_token;
            } else{
                return "error";
            }
        });
    } else {
        fetch('/api/request_token', {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json())
        .then(tokenData => {
            if (tokenData.publish_token) {
                return tokenData.publish_token;
            } else{
                return "error";
            }
        });
    }
}