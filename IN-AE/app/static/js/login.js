document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const inputs = document.querySelectorAll('input');

    // 입력 필드 포커스 효과
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    // 폼 제출 처리
    loginForm.addEventListener('submit', async function(e) {
        const submitButton = this.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.textContent = 'try to login...';

        try {
            // 폼 제출은 HTML form action으로 처리됨
            return true;
        } catch (error) {
            console.error('Error:', error);
            alert('login failed');
            submitButton.disabled = false;
            submitButton.textContent = 'login';
            return false;
        }
    });
});
