// Функция для получения значения куки
function getCookie(name) {
    return document.cookie
        .split(';')
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith(`${name}=`))
        ?.split('=')[1] || null;
}

// Функция для создания запроса с обработкой ошибок
async function sendRequest(url, method, body = null, jwtToken = null) {
    const headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    };

    if (jwtToken) {
        // JWT передаём через Authorization (рекомендуется)
        headers['Authorization'] = `Bearer ${jwtToken}`;
    }

    try {
        const response = await fetch(url, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
        });

        // Обработка ошибок
        if (!response.ok) {
            let errorData = {};
            try {
                errorData = await response.json();
            } catch (jsonError) {
                console.error('Ошибка парсинга JSON:', jsonError);
            }
            throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            console.error('Сетевая ошибка или проблема с CORS:', error);
        }
        console.error(`Ошибка в запросе: ${error.message}`);
        throw error;
    }
}

// Инициализация данных
document.addEventListener('DOMContentLoaded', () => {
    const articleContainer = document.querySelector('.article-container');
    if (!articleContainer) {
        console.error('Элемент .article-container не найден. Убедитесь, что он присутствует в DOM.');
        return;
    }

    const BLOG_DATA = {
        id: articleContainer.dataset.blogId,
        status: articleContainer.dataset.blogStatus,
        author: articleContainer.dataset.blogAuthor,
        jwtToken: getCookie('users_access_token'),
    };

    console.log('BLOG_DATA:', BLOG_DATA);

    // Обработчик удаления
    const deleteButton = document.querySelector('[data-action="delete"]');
    if (deleteButton) {
        deleteButton.addEventListener('click', () => {
            if (confirm('Вы уверены, что хотите удалить этот блог?')) {
                deleteBlog(BLOG_DATA);
            }
        });
    }

    // Обработчик изменения статуса
    const statusButton = document.querySelector('[data-action="change-status"]');
    if (statusButton) {
        statusButton.addEventListener('click', () => {
            const newStatus = statusButton.dataset.newStatus;
            changeBlogStatus(BLOG_DATA, newStatus);
        });
    }
});

// Функция для удаления блога
async function deleteBlog({id, jwtToken}) {
    try {
        await sendRequest(`/api/delete_blog/${id}`, 'DELETE', null, jwtToken);
        alert('Блог успешно удалён. Перенаправление...');
        window.location.href = '/blogs/';
    } catch (error) {
        console.error('Не удалось удалить блог:', error);
    }
}

// Функция для изменения статуса блога
async function changeBlogStatus({id, jwtToken}, newStatus) {
    try {
        // Передаём new_status как часть строки запроса
        const url = `/api/change_blog_status/${id}?new_status=${encodeURIComponent(newStatus)}`;
        await sendRequest(url, 'PATCH', null, jwtToken);
        alert('Статус успешно изменён. Страница будет обновлена.');
        location.reload(); // Обновляем страницу
    } catch (error) {
        console.error('Не удалось изменить статус блога:', error);
        alert('Ошибка при изменении статуса блога. Попробуйте ещё раз.');
    }
}
