document.addEventListener('DOMContentLoaded', (event) => {
    // Odtwarzanie stanu checkboxów
    const selectedSubcats = localStorage.getItem('selectedSubcats') ? JSON.parse(localStorage.getItem('selectedSubcats')) : [];

    document.querySelectorAll('input[name="subcat"]').forEach((checkbox) => {
        checkbox.checked = selectedSubcats.includes(checkbox.value);
        
        // Zapisywanie stanu checkboxów
        checkbox.addEventListener('change', () => {
            const subcatId = checkbox.value;
            if (checkbox.checked) {
                if (!selectedSubcats.includes(subcatId)) {
                    selectedSubcats.push(subcatId);
                }
            } else {
                const index = selectedSubcats.indexOf(subcatId);
                if (index > -1) {
                    selectedSubcats.splice(index, 1);
                }
            }
            localStorage.setItem('selectedSubcats', JSON.stringify(selectedSubcats));
        });
    });
});