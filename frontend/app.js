const apiBase = window.API_BASE_URL || "http://localhost:8001";

// Глобальное состояние интерфейса: сессия пользователя и загруженный каталог.
let token = localStorage.getItem("warehouse_token") || "";
let currentRole = localStorage.getItem("warehouse_role") || "";
let currentUser = null;
let products = [];

// Основные DOM-узлы, с которыми работает приложение.
const sessionInfo = document.querySelector("#sessionInfo");
const toast = document.querySelector("#toast");
const loginForm = document.querySelector("#loginForm");
const profileBox = document.querySelector("#profileBox");
const profileName = document.querySelector("#profileName");
const profileRole = document.querySelector("#profileRole");
const productsBody = document.querySelector("#productsBody");
const ordersBody = document.querySelector("#ordersBody");
const movementsList = document.querySelector("#movementsList");
const orderProduct = document.querySelector("#orderProduct");
const orderQuantity = document.querySelector("#orderQuantity");
const orderStockHint = document.querySelector("#orderStockHint");
const movementProduct = document.querySelector("#movementProduct");
const categoryFilter = document.querySelector("#categoryFilter");

function notify(message) {
  // Единый короткий toast для результата операций.
  toast.textContent = message;
  toast.hidden = false;
  setTimeout(() => {
    toast.hidden = true;
  }, 3000);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function request(path, options = {}) {
  // Общая обертка над fetch: добавляет токен, отключает кеш и нормализует ошибки.
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    const detail = Array.isArray(error.detail)
      ? error.detail.map((item) => item.msg || JSON.stringify(item)).join("; ")
      : error.detail;
    throw new Error(humanizeError(detail || "Ошибка запроса"));
  }
  if (response.status === 204) return null;
  return response.json();
}

function humanizeError(message) {
  const text = String(message);
  if (text.includes("Not enough stock for product")) {
    const sku = text.replace("Not enough stock for product", "").trim();
    return `Не хватает остатка для товара ${sku}. Уменьшите количество или сделайте приход.`;
  }
  if (text.includes("Not enough stock")) {
    return "Не хватает остатка на складе.";
  }
  return text;
}

function formPayload(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  for (const key of ["quantity", "min_quantity", "product_id"]) {
    if (key in data) data[key] = Number(data[key]);
  }
  return data;
}

function setActiveTab(tabName) {
  // Переключение вкладок без перезагрузки страницы.
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `${tabName}Tab`);
  });
}

function clearSession() {
  // Выход из аккаунта очищает локальное состояние и localStorage.
  token = "";
  currentRole = "";
  currentUser = null;
  localStorage.removeItem("warehouse_token");
  localStorage.removeItem("warehouse_role");
  updateSession();
}

function updateSession() {
  // Перерисовка правой части шапки: форма входа или профиль пользователя.
  const loggedIn = Boolean(token && currentUser);
  loginForm.hidden = loggedIn;
  profileBox.hidden = !loggedIn;

  if (loggedIn) {
    sessionInfo.textContent = "Рабочая панель";
    profileName.textContent = currentUser.full_name || currentUser.username;
    profileRole.textContent = `@${currentUser.username} · ${currentUser.role}`;
    return;
  }

  sessionInfo.textContent = "Войдите в систему";
  profileName.textContent = "Пользователь";
  profileRole.textContent = "";
}

function productLabel(product) {
  // Человекочитаемое имя товара для заказов и движений.
  if (!product) return "Товар не найден";
  return `${product.sku} · ${product.name}`;
}

function movementTypeLabel(type) {
  return {
    inbound: "Приход",
    outbound: "Расход",
    adjustment: "Инвентаризация",
  }[type] || type;
}

function statusLabel(status) {
  return {
    draft: "Черновик",
    reserved: "Зарезервирован",
    shipped: "Отгружен",
    cancelled: "Отменен",
  }[status] || status;
}

function renderProductOptions() {
  // Списки товаров в формах заказа и складского движения.
  const options = products
    .map(
      (product) =>
        `<option value="${product.id}">${escapeHtml(product.sku)} · ${escapeHtml(product.name)} (${product.quantity} шт.)</option>`,
    )
    .join("");
  orderProduct.innerHTML = options;
  movementProduct.innerHTML = options;
  updateOrderAvailability();
}

function selectedOrderProduct() {
  return products.find((product) => product.id === Number(orderProduct.value));
}

function updateOrderAvailability() {
  const product = selectedOrderProduct();
  if (!product) {
    orderQuantity.removeAttribute("max");
    orderStockHint.textContent = "Выберите товар";
    orderStockHint.classList.remove("warning");
    return;
  }

  orderQuantity.max = product.quantity;
  orderStockHint.textContent = `Доступно для заказа: ${product.quantity} шт.`;
  const requested = Number(orderQuantity.value || 0);
  const tooMuch = requested > product.quantity;
  orderStockHint.classList.toggle("warning", tooMuch || product.quantity === 0);
  if (tooMuch) {
    orderStockHint.textContent = `На складе только ${product.quantity} шт. Уменьшите количество.`;
  }
}

function renderCategoryFilter() {
  // Фильтр строится из фактических категорий загруженного каталога.
  const selected = categoryFilter.value;
  const categories = [...new Set(products.map((product) => product.category))].sort((a, b) =>
    a.localeCompare(b, "ru"),
  );
  categoryFilter.innerHTML = [
    '<option value="">Все категории</option>',
    ...categories.map(
      (category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`,
    ),
  ].join("");
  categoryFilter.value = categories.includes(selected) ? selected : "";
}

function renderProducts() {
  // Таблица товаров учитывает выбранную категорию и показывает понятный остаток.
  const selectedCategory = categoryFilter.value;
  const visibleProducts = selectedCategory
    ? products.filter((product) => product.category === selectedCategory)
    : products;

  productsBody.innerHTML = visibleProducts
    .map((product) => {
      const qtyClass = product.quantity <= product.min_quantity ? "low" : "";
      return `<tr>
        <td>${escapeHtml(product.sku)}</td>
        <td>${escapeHtml(product.name)}</td>
        <td>${escapeHtml(product.category)}</td>
        <td>${escapeHtml(product.location)}</td>
        <td class="${qtyClass}">
          <span class="stock-value">Доступно: ${product.quantity} шт.</span>
          <span class="stock-min">Минимум: ${product.min_quantity} шт.</span>
        </td>
        <td><button data-delete-product="${product.id}" class="danger" type="button">Удалить</button></td>
      </tr>`;
    })
    .join("");
}

async function loadProducts() {
  // Загрузка товаров обновляет таблицу, фильтр и выпадающие списки.
  products = await request("/products");
  renderCategoryFilter();
  renderProducts();
  renderProductOptions();
}

async function loadOrders() {
  // Заказы отображаются с вложенными товарами, а не с техническими id.
  const orders = await request("/orders");
  ordersBody.innerHTML = orders
    .map((order) => {
      const items = order.items
        .map(
          (item) =>
            `<span class="item-line">${escapeHtml(productLabel(item.product))}<strong>${item.quantity} шт.</strong></span>`,
        )
        .join("");
      const canShip = currentRole !== "clerk" && order.status !== "shipped";
      return `<tr>
        <td>${order.id}</td>
        <td>${escapeHtml(order.customer_name)}</td>
        <td><span class="status-pill">${escapeHtml(statusLabel(order.status))}</span></td>
        <td class="item-list">${items}</td>
        <td>${canShip ? `<button data-ship="${order.id}" class="secondary" type="button">Отгрузить</button>` : ""}</td>
        <td><button data-delete-order="${order.id}" class="danger" type="button">Удалить</button></td>
      </tr>`;
    })
    .join("");
}

async function loadMovements() {
  // История склада отображается как журнал операций для оператора.
  const movements = await request("/movements");
  movementsList.innerHTML = movements
    .map(
      (movement) =>
        `<li>
          <div class="feed-head">
            <strong>${escapeHtml(movementTypeLabel(movement.movement_type))}</strong>
            <span>${new Date(movement.created_at).toLocaleString("ru-RU")}</span>
          </div>
          <div>${escapeHtml(productLabel(movement.product))}</div>
          <div class="feed-meta">Количество: ${movement.quantity} шт.${movement.comment ? ` · ${escapeHtml(movement.comment)}` : ""}</div>
          <button data-delete-movement="${movement.id}" class="danger compact" type="button">Удалить</button>
        </li>`,
    )
    .join("");
}

async function refreshAfterChange(tabName) {
  // После CRUD-операции подтягиваем все зависимые списки без reload страницы.
  await loadAll();
  setActiveTab(tabName);
}

async function loadProfile() {
  // Проверка сохраненной сессии при открытии страницы.
  if (!token) {
    updateSession();
    return;
  }

  try {
    currentUser = await request("/me");
    currentRole = currentUser.role;
    localStorage.setItem("warehouse_role", currentRole);
    updateSession();
  } catch (error) {
    clearSession();
    notify("Сессия истекла, войдите снова");
  }
}

async function loadAll() {
  // Первичная и повторная загрузка рабочих данных.
  if (!token) return;
  await Promise.all([loadProducts(), loadOrders(), loadMovements()]);
}

document.querySelectorAll(".tab-button").forEach((button) => {
  button.addEventListener("click", () => setActiveTab(button.dataset.tab));
});

loginForm.addEventListener("submit", async (event) => {
  // Авторизация: сохраняем токен, загружаем профиль и рабочие списки.
  event.preventDefault();
  const payload = formPayload(event.currentTarget);
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  token = data.access_token;
  currentRole = data.role;
  localStorage.setItem("warehouse_token", token);
  localStorage.setItem("warehouse_role", currentRole);
  await loadProfile();
  notify("Вход выполнен");
  await loadAll();
});

document.querySelector("#logoutButton").addEventListener("click", () => {
  // Выход очищает таблицы, чтобы старые данные не оставались после завершения сессии.
  clearSession();
  productsBody.innerHTML = "";
  ordersBody.innerHTML = "";
  movementsList.innerHTML = "";
  orderProduct.innerHTML = "";
  movementProduct.innerHTML = "";
  notify("Вы вышли из аккаунта");
});

document.querySelector("#productForm").addEventListener("submit", async (event) => {
  // Создание товара с мгновенным обновлением таблицы и фильтра.
  event.preventDefault();
  const form = event.currentTarget;
  await request("/products", {
    method: "POST",
    body: JSON.stringify(formPayload(form)),
  });
  form.reset();
  notify("Товар добавлен");
  await refreshAfterChange("products");
});

document.querySelector("#orderForm").addEventListener("submit", async (event) => {
  // Создание заказа из одной выбранной позиции.
  event.preventDefault();
  const form = event.currentTarget;
  try {
    const data = formPayload(form);
    const product = selectedOrderProduct();
    if (product && data.quantity > product.quantity) {
      notify(`На складе только ${product.quantity} шт. Уменьшите количество.`);
      updateOrderAvailability();
      return;
    }
    await request("/orders", {
      method: "POST",
      body: JSON.stringify({
        customer_name: data.customer_name,
        items: [{ product_id: data.product_id, quantity: data.quantity }],
      }),
    });
    form.reset();
    notify("Заказ создан");
    await refreshAfterChange("orders");
  } catch (error) {
    notify(error.message);
  }
});

document.querySelector("#movementForm").addEventListener("submit", async (event) => {
  // Ручное проведение прихода, расхода или инвентаризации.
  event.preventDefault();
  const form = event.currentTarget;
  await request("/movements", {
    method: "POST",
    body: JSON.stringify(formPayload(form)),
  });
  form.reset();
  notify("Движение проведено");
  await refreshAfterChange("movements");
});

ordersBody.addEventListener("click", async (event) => {
  // Делегированные действия в таблице заказов: отгрузка и удаление.
  const shipButton = event.target.closest("[data-ship]");
  if (shipButton) {
    await request(`/orders/${shipButton.dataset.ship}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "shipped" }),
    });
    notify("Заказ отгружен");
    await refreshAfterChange("orders");
    return;
  }

  const deleteButton = event.target.closest("[data-delete-order]");
  if (!deleteButton) return;
  if (!confirm("Удалить заказ?")) return;
  await request(`/orders/${deleteButton.dataset.deleteOrder}`, {
    method: "DELETE",
  });
  notify("Заказ удален");
  await refreshAfterChange("orders");
});

productsBody.addEventListener("click", async (event) => {
  // Делегированное удаление товара из таблицы.
  const button = event.target.closest("[data-delete-product]");
  if (!button) return;
  if (!confirm("Удалить товар?")) return;
  await request(`/products/${button.dataset.deleteProduct}`, {
    method: "DELETE",
  });
  notify("Товар удален");
  await refreshAfterChange("products");
});

movementsList.addEventListener("click", async (event) => {
  // Делегированное удаление записи из журнала складских движений.
  const button = event.target.closest("[data-delete-movement]");
  if (!button) return;
  if (!confirm("Удалить движение склада?")) return;
  await request(`/movements/${button.dataset.deleteMovement}`, {
    method: "DELETE",
  });
  notify("Движение удалено");
  await refreshAfterChange("movements");
});

document.querySelector("#reloadProducts").addEventListener("click", loadProducts);
document.querySelector("#reloadOrders").addEventListener("click", loadOrders);
document.querySelector("#reloadMovements").addEventListener("click", loadMovements);
orderProduct.addEventListener("change", updateOrderAvailability);
orderQuantity.addEventListener("input", updateOrderAvailability);
categoryFilter.addEventListener("change", renderProducts);

updateSession();
loadProfile().then(loadAll).catch((error) => notify(error.message));
