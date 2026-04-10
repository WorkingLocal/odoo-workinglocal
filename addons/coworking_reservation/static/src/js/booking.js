/* Working Local — Booking form interactie */

document.addEventListener('DOMContentLoaded', () => {

    // Vrije bijdrage selectie
    document.querySelectorAll('.contribution-option').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.contribution-option').forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            const amount = btn.dataset.amount;
            const input = document.getElementById('contribution_amount');
            if (input) {
                input.value = amount === 'custom' ? '' : amount;
                if (amount === 'custom') input.focus();
            }
        });
    });

    // Duur berekening tonen
    const startInput = document.getElementById('start_datetime');
    const endInput = document.getElementById('end_datetime');
    const durationEl = document.getElementById('duration_display');

    function updateDuration() {
        if (!startInput?.value || !endInput?.value || !durationEl) return;
        const start = new Date(startInput.value);
        const end = new Date(endInput.value);
        const hours = (end - start) / 3600000;
        if (hours > 0) {
            durationEl.textContent = hours === 1 ? '1 uur' : `${hours.toFixed(1)} uur`;
        }
    }

    startInput?.addEventListener('change', updateDuration);
    endInput?.addEventListener('change', updateDuration);
});
