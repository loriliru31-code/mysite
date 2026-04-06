document.addEventListener("DOMContentLoaded", () => {
    // Получаем товары в корзине с сервера через data-cart
    const cartProducts = JSON.parse(document.getElementById("cart-count").dataset.items || "[]");

    function updateCartButtons() {
        document.querySelectorAll(".btn-cart").forEach(btn => {
            const productId = parseInt(btn.dataset.id);

            if (cartProducts.includes(productId)) {
                // Товар уже в корзине
                btn.textContent = "Перейти в корзину";
                btn.style.background = "#999"; // серый цвет
                btn.style.cursor = "pointer";
                btn.href = "/cart";
                btn.removeEventListener("click", addToCartHandler);
            } else {
                // Товар не в корзине
                btn.textContent = "В корзину";
                btn.style.background = "#8C2F39";
                btn.style.cursor = "pointer";
                btn.href = "#";
                btn.addEventListener("click", addToCartHandler);
            }
        });
    }

    function addToCartHandler(e) {
        e.preventDefault();
        const btn = e.currentTarget;
        const productId = btn.dataset.id;

        fetch(`/add_to_cart/${productId}`, { method: "POST" })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // обновляем счётчик корзины
                    const cartCounter = document.getElementById("cart-count");
                    if (cartCounter) {
                        cartCounter.textContent = data.cart_count;
                        cartProducts.push(parseInt(productId)); // добавляем в локальный массив
                        updateCartButtons(); // обновляем кнопки
                    }
                }
                // Ошибки можно залогировать в консоль, если нужно
                else console.error("Ошибка при добавлении товара");
            });
    }

    updateCartButtons();
});