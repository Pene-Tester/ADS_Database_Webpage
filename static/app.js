document.addEventListener("DOMContentLoaded", function () {
    // Fetch and display the inventory when the page loads
    fetchInventory();

    // Event listener for form submission
    document.getElementById("inventory-form").addEventListener("submit", async function (e) {
        e.preventDefault(); // Prevent the default form submission

        const itemName = document.getElementById("item-name").value;
        const quantity = document.getElementById("item-quantity").value;
        const price = document.getElementById("item-price").value;

        // Prepare the item data
        const itemData = {
            item_name: itemName,
            quantity: parseInt(quantity),
            price: parseFloat(price)
        };

        // Send the data to the server
        const response = await fetch("/api/add_item", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(itemData)
        });

        if (response.ok) {
            console.log("Item added successfully");
            fetchInventory(); // Refresh the inventory display
            document.getElementById("inventory-form").reset(); // Reset the form
        } else {
            console.error("Failed to add item:", await response.text());
        }
    });
});

// Function to fetch inventory items and update the table
async function fetchInventory() {
    const response = await fetch("/api/items");
    const data = await response.json();

    const tbody = document.querySelector("#inventory-table tbody");
    tbody.innerHTML = ""; // Clear the table body
    data.forEach((item) => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${item.id}</td>
            <td>${item.item_name}</td>
            <td>${item.quantity}</td>
            <td>${item.price}</td>
            <td>
                <button onclick="deleteItem(${item.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row); // Append the new row to the table body
    });
}

// Function to delete an item from the inventory
async function deleteItem(id) {
    await fetch(`/api/delete_item/${id}`, { method: "DELETE" });
    fetchInventory(); // Refresh the inventory display after deletion
}
