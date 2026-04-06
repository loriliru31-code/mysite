const categorySelect = document.getElementById("categorySelect");
const filterOptions = document.getElementById("filterOptions");

// Получаем category из URL
const urlParams = new URLSearchParams(window.location.search);
const categoryFromUrl = urlParams.get("category");

if (categoryFromUrl) {
    categorySelect.value = categoryFromUrl;
    categorySelect.dispatchEvent(new Event("change"));

    setTimeout(() => {
        document.querySelector(".apply-btn").click();
    }, 200);
}

// Обновление фильтров по выбору категории
categorySelect.addEventListener("change", () => {
    const categoryId = categorySelect.value;

    if (categoryId === "") {
        filterOptions.innerHTML = "";
        return;
    }

    fetch(`/api/attributes/${categoryId}`)
        .then(res => res.json())
        .then(data => {
            filterOptions.innerHTML = "";

            data.forEach(attr => {
                const select = document.createElement("select");
                select.dataset.id = attr.id;

                let options = `<option value="">${attr.name}</option>`;
                attr.values.forEach(v => {
                    options += `<option value="${v}">${v}</option>`;
                });

                select.innerHTML = options;
                filterOptions.appendChild(select);
            });
        });
});

// Применение фильтров
document.querySelector(".apply-btn").addEventListener("click", () => {
    const categoryId = categorySelect.value;
    const selects = document.querySelectorAll("#filterOptions select");

    let filters = {};
    selects.forEach(s => {
        if (s.value !== "") {
            filters[s.dataset.id] = s.value;
        }
    });

    fetch("/api/filter_products", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category_id: categoryId, filters: filters })
    })
        .then(res => res.json())
        .then(products => {
            const catalog = document.getElementById("catalog");

            // Ищем контейнер grid, если его нет — создаём
            let grid = catalog.querySelector(".catalog-products-grid");
            if (!grid) {
                grid = document.createElement("div");
                grid.className = "catalog-products-grid";
                catalog.appendChild(grid);
            }

            // Очищаем старые карточки
            grid.innerHTML = "";

            // Создаём новые карточки
            products.forEach(p => {
                const card = document.createElement("article");
                card.className = "product-card";

                card.innerHTML = `
                    <div class="product-img">
                        ${p.image ? `<img src="/static/${p.image}" alt="${p.name}">` : '<div class="placeholder-img"></div>'}
                    </div>
                    <p class="product-title">${p.name}</p>
                    <p>${p.price} ₽</p>
                    <a href="/add_to_cart/${p.id}" class="btn-cart">В корзину</a>
                `;

                grid.appendChild(card);
            });
        });
});