$(document).ready(function() {
    $('#search-input').on('input', function() {
        var query = $(this).val();
        if (query.length >= 1) {
            $.ajax({
                url: '/search',
                type: 'GET',
                data: { query: query },
                success: function(response) {
                    displaySuggestions(response);
                },
                error: function(error) {
                    console.error('Error fetching suggestions:', error);
                }
            });
        } else {
            $('#suggestions').empty();
            RemoveProduct();
        }
    });

    function displaySuggestions(suggestions) {
        var suggestionsDiv = $('#suggestions');
        suggestionsDiv.empty();
        const suggestionsLength = Object.keys(suggestions).length;
        if (suggestionsLength > 0) {
            var suggestionList = $('<ul></ul>');
            RemoveProduct();
            var progressStep = 100 / suggestionsLength;
            var currentProgress = 0;
            updateProgress(currentProgress);
            var completedRequests = 0;

            Object.entries(suggestions).forEach(([key, value]) => {
                // Adding an icon to the list item
                var listItem = $(`
                    <a href="/product/${key}">
                        <li>
                            <i class="fas fa-search"></i> ${value}
                        </li>
                    </a>
                `);
                suggestionList.append(listItem);

                $.ajax({
                    url: '/search/get',
                    type: 'GET',
                    data: { query: key },
                    success: function(response) {
                        AddProduct(response, key);
                        completedRequests++;
                        currentProgress += progressStep;
                        updateProgress(currentProgress);

                        // Ensure the progress bar reaches 100% after the last request
                        if (completedRequests === suggestionsLength) {
                            updateProgress(100);
                        }
                    },
                    error: function(error) {
                        console.error('Error fetching product details:', error);
                    }
                });
            });

            suggestionsDiv.append(suggestionList);
        } else {
            suggestionsDiv.html('<p>لا توجد نتائج</p>');
            RemoveProduct();
        }
    }

    function RemoveProduct() {
        const cart = document.getElementById('products');
        while (cart.firstChild) {
            cart.removeChild(cart.firstChild);
        }
    }

    function AddProduct(data, key) {
        const cart = $('#products');
        let items = '';
        data['img'].forEach(item => {
            items += `<img id="images" src="${item}" alt="Image not available">`;
        });
        var product = `
            <div class="product">
                <a href="/product/${key}">
                    <h2><span>المنتج : <br></span>${data['product_name']}</h2>
                    <div class="images">${items}</div>
                    <div class="product-info">
                        <ul>
                            <li><p><span>موصفات المنتج: <br></span>${data['info']}</p></li>
                            <li><p><span>الكمية المتوفرة: <br></span>${data['qnt']}</p></li>
                            <li><p><span>السعر: <br></span>${data['price']} DA</p></li>
                        </ul>
                    </div>
                    <button>عرض المنتج</button>
                </a>
            </div>`;
        cart.append(product);
    }

    function updateProgress(width) {
        let elem = document.getElementById("filler");
        elem.style.width = width + "%";
        elem.innerHTML = width.toFixed(2) + '%';
        elem.style.color = 'black';
    }
});
