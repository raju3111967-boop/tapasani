/**
 * तपासणी मेमो - Auto Calculation Logic
 * Frontend JS for real-time field calculations
 */

document.addEventListener('DOMContentLoaded', function() {
    // --- Auto Calculation Fields ---
    const calcFields = [
        'id_market_value', 'id_consideration_amount',
        'id_stamp_duty_collected', 'id_stamp_duty_actual',
        'id_reg_fee_collected', 'id_reg_fee_actual',
        'id_recovered_stamp_duty', 'id_recovered_reg_fee', 'id_recovered_penalty',
        'id_execution_date',
        'id_penalty_date', 'id_penalty_rate'
    ];

    // Result display fields
    const resultFields = {
        valuation_difference: document.getElementById('id_valuation_difference'),
        stamp_duty_short: document.getElementById('display_stamp_duty_short'),
        reg_fee_short: document.getElementById('display_reg_fee_short'),
        total_short: document.getElementById('display_total_short'),
        total_months: document.getElementById('display_total_months'),
        penalty_amount: document.getElementById('display_penalty_amount'),
        total_amount: document.getElementById('display_total_amount'),
        balance_amount: document.getElementById('display_balance_amount'),
        balance_stamp_duty: document.getElementById('id_balance_stamp_duty'),
        balance_reg_fee: document.getElementById('id_balance_reg_fee'),
        balance_penalty: document.getElementById('id_balance_penalty'),
    };

    function getVal(id) {
        const el = document.getElementById(id);
        if (!el) return 0;
        return parseFloat(el.value) || 0;
    }

    function formatNumber(num) {
        return parseFloat(num).toFixed(2);
    }

    function calculate() {
        const marketValue = getVal('id_market_value');
        const considerationAmount = getVal('id_consideration_amount');
        const stampActual = getVal('id_stamp_duty_actual');
        const stampCollected = getVal('id_stamp_duty_collected');
        const feeActual = getVal('id_reg_fee_actual');
        const feeCollected = getVal('id_reg_fee_collected');
        const recoveredStampDuty = getVal('id_recovered_stamp_duty');
        const recoveredRegFee = getVal('id_recovered_reg_fee');
        const recoveredPenalty = getVal('id_recovered_penalty');
        const penaltyRate = getVal('id_penalty_rate') || 0.02;

        // मुल्याकंनातील फरक = आक्षेपीत मुल्याकंन - दस्तातील मोबदला
        const valuationDifference = Math.max(0, marketValue - considerationAmount);

        // कमी मु.शु
        const stampShort = Math.max(0, stampActual - stampCollected);
        // कमी फी
        const feeShort = Math.max(0, feeActual - feeCollected);
        // एकुण कमी
        const totalShort = stampShort + feeShort;

        // एकुण महिने (from execution date to penalty date or today, round up)
        let totalMonths = 0;
        const execDateEl = document.getElementById('id_execution_date');
        const penaltyDateEl = document.getElementById('id_penalty_date');
        
        if (execDateEl && execDateEl.value) {
            const execDate = new Date(execDateEl.value);
            let endDate;
            
            // Use penalty_date if available, otherwise use today
            if (penaltyDateEl && penaltyDateEl.value) {
                endDate = new Date(penaltyDateEl.value);
            } else {
                endDate = new Date();
            }
            
            const diffTime = endDate - execDate;
            const diffDays = Math.max(0, Math.floor(diffTime / (1000 * 60 * 60 * 24)));
            totalMonths = diffDays > 0 ? Math.ceil(diffDays / 30) : 0;
        }

        // शास्ती = एकुण कमी × दर × महिने
        const penalty = totalShort * penaltyRate * totalMonths;
        // एकुण रक्कम
        const totalAmount = totalShort + penalty;

        // Individual balances
        const balanceStampDuty = Math.max(0, stampShort - recoveredStampDuty);
        const balanceRegFee = Math.max(0, feeShort - recoveredRegFee);
        const balancePenalty = Math.max(0, penalty - recoveredPenalty);

        // Total recovered and balance
        const totalRecovered = recoveredStampDuty + recoveredRegFee + recoveredPenalty;
        const balance = totalAmount - totalRecovered;

        // Update display fields
        if (resultFields.valuation_difference) {
            resultFields.valuation_difference.value = formatNumber(valuationDifference);
        }
        if (resultFields.stamp_duty_short) resultFields.stamp_duty_short.textContent = '₹ ' + formatNumber(stampShort);
        if (resultFields.reg_fee_short) resultFields.reg_fee_short.textContent = '₹ ' + formatNumber(feeShort);
        if (resultFields.total_short) resultFields.total_short.textContent = '₹ ' + formatNumber(totalShort);
        if (resultFields.total_months) resultFields.total_months.textContent = totalMonths + ' महिने';
        if (resultFields.penalty_amount) resultFields.penalty_amount.textContent = '₹ ' + formatNumber(penalty);
        if (resultFields.total_amount) resultFields.total_amount.textContent = '₹ ' + formatNumber(totalAmount);
        if (resultFields.balance_amount) {
            resultFields.balance_amount.textContent = '₹ ' + formatNumber(balance);
            resultFields.balance_amount.className = balance > 0 ? 'calc-result text-danger fw-bold' : 'calc-result text-success fw-bold';
        }
        // Update individual balance fields
        if (resultFields.balance_stamp_duty) {
            resultFields.balance_stamp_duty.value = '₹ ' + formatNumber(balanceStampDuty);
            resultFields.balance_stamp_duty.className = balanceStampDuty > 0 ? 'form-control text-danger fw-bold' : 'form-control text-success fw-bold';
        }
        if (resultFields.balance_reg_fee) {
            resultFields.balance_reg_fee.value = '₹ ' + formatNumber(balanceRegFee);
            resultFields.balance_reg_fee.className = balanceRegFee > 0 ? 'form-control text-danger fw-bold' : 'form-control text-success fw-bold';
        }
        if (resultFields.balance_penalty) {
            resultFields.balance_penalty.value = '₹ ' + formatNumber(balancePenalty);
            resultFields.balance_penalty.className = balancePenalty > 0 ? 'form-control text-danger fw-bold' : 'form-control text-success fw-bold';
        }

        // --- Update Recovery Letter Button State ---
        const btnRecoveryLetter = document.getElementById('id_btn_recovery_letter');
        if (btnRecoveryLetter) {
            const hasRecovery = recoveredStampDuty > 0 || recoveredRegFee > 0 || recoveredPenalty > 0;
            const isEdit = btnRecoveryLetter.getAttribute('href') !== '#';
            
            if (hasRecovery && isEdit) {
                btnRecoveryLetter.classList.remove('disabled');
                btnRecoveryLetter.style.pointerEvents = 'auto';
                btnRecoveryLetter.style.opacity = '1';
            } else {
                btnRecoveryLetter.classList.add('disabled');
                btnRecoveryLetter.style.pointerEvents = 'none';
                btnRecoveryLetter.style.opacity = '0.6';
            }
        }
    }

    // Bind event listeners
    calcFields.forEach(function(fieldId) {
        const el = document.getElementById(fieldId);
        if (el) {
            el.addEventListener('input', calculate);
            el.addEventListener('change', calculate);
        }
    });

    // Initial calculation on page load
    calculate();

    // --- Sidebar Toggle (Mobile) ---
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // --- Search Box Focus ---
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keyup', function(e) {
            if (e.key === 'Enter') {
                this.closest('form').submit();
            }
        });
    }

    // --- Litigation Status Conditional Fields ---
    const litigationStatusEl = document.getElementById('id_litigation_status');
    const litigationFieldsDiv = document.getElementById('litigation-fields');

    function toggleLitigationFields() {
        if (litigationStatusEl && litigationFieldsDiv) {
            // Show litigation fields only if litigation status is "न्याय प्रविष्ट"
            const statusValue = litigationStatusEl.value;
            if (statusValue && statusValue === 'न्याय प्रविष्ट') {
                litigationFieldsDiv.style.display = 'block';
            } else {
                litigationFieldsDiv.style.display = 'none';
            }
        }
    }

    if (litigationStatusEl) {
        litigationStatusEl.addEventListener('change', toggleLitigationFields);
        // Check on page load
        toggleLitigationFields();
    }
});
