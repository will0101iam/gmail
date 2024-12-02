document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const username = this.querySelector('input[type="text"]').value;
    const password = this.querySelector('input[type="password"]').value;

    // 普通登录逻辑
    fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });
});

// Google登录
document.querySelector('.gmail-btn').addEventListener('click', () => {
    // 重定向到Google登录
    window.location.href = 'http://localhost:5000/login';
});

// 检查用户登录状态
function checkLoginStatus() {
    fetch('http://localhost:5000/user')
        .then(response => response.json())
        .then(user => {
            if (user.email) {
                // 已登录
                console.log('已登录:', user);
            }
        })
        .catch(error => {
            // 未登录
            console.log('未登录');
        });
}

// 页面加载时检查
checkLoginStatus();