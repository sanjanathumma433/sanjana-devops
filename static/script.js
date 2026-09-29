let currentStep = 1;

function nextStep(step) {
    // Hide all steps
    document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
    // Show current
    document.getElementById(`step-${step}`).classList.add('active');
    
    // Update Stepper UI
    document.querySelectorAll('.step').forEach((el, idx) => {
        if (idx < step) el.classList.add('active');
        else el.classList.remove('active');
    });

    currentStep = step;
}

function toggleSecuredFields() {
    const isSecured = document.getElementById('is_secured').value === 'Y';
    document.getElementById('secured_fields').style.display = isSecured ? 'block' : 'none';
    document.getElementById('unsecured_fields').style.display = isSecured ? 'none' : 'block';
}

function toggleEmploymentFields() {
    const empType = document.getElementById('employment').value;
    document.getElementById('surety_field').style.display = (empType === '2') ? 'block' : 'none';
}

async function submitForm() {
    const loader = document.getElementById('loader');
    const form = document.getElementById('loanForm');
    const resultDiv = document.getElementById('result');
    const resultContent = document.getElementById('result-content');

    const formData = {
        age: document.getElementById('age').value,
        credit_score: document.getElementById('credit_score').value,
        is_secured: document.getElementById('is_secured').value,
        loan_amount: document.getElementById('loan_amount').value,
        collateral_value: document.getElementById('collateral_value').value,
        tenure: document.getElementById('tenure').value,
        interest_rate: document.getElementById('interest_rate').value,
        employment: document.getElementById('employment').value,
        has_surety: document.getElementById('has_surety_cb').checked ? 'Y' : 'N',
        salary: document.getElementById('salary').value,
        existing_emi: document.getElementById('existing_emi').value
    };

    form.style.display = 'none';
    loader.style.display = 'block';

    try {
        const response = await fetch('/check-eligibility', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        loader.style.display = 'none';
        resultDiv.style.display = 'block';

        if (data.status === 'approved') {
            resultContent.innerHTML = `
                <div class="res-approved">
                    <i class="fas fa-circle-check fa-4x"></i>
                    <h2 style="margin-top:20px">Application Pre-Approved</h2>
                    <p>${data.message}</p>
                </div>`;
        } else if (data.status === 'retry') {
            resultContent.innerHTML = `
                <div style="color: #f59e0b">
                    <i class="fas fa-triangle-exclamation fa-4x"></i>
                    <h2 style="margin-top:20px">Limit Exceeded</h2>
                    <p>${data.reason}</p>
                </div>`;
        } else {
            resultContent.innerHTML = `
                <div class="res-rejected">
                    <i class="fas fa-circle-xmark fa-4x"></i>
                    <h2 style="margin-top:20px">Application Declined</h2>
                    <p>${data.reason}</p>
                </div>`;
        }
    } catch (e) {
        alert("Connection failed.");
        location.reload();
    }
}
function calculateEMI() {
    const loanAmount = parseFloat(document.getElementById('loan_amount').value) || 0;
    const interestRate = parseFloat(document.getElementById('interest_rate').value) || 0;
    const tenure = parseFloat(document.getElementById('tenure').value) || 0;

    const emiDisplay = document.getElementById('emi_amount');

    if (loanAmount <= 0 || interestRate <= 0 || tenure <= 0) {
        emiDisplay.textContent = '₹0';
        return;
    }

    const monthlyRate = interestRate / 12 / 100;
    const numberOfMonths = tenure * 12;

    const emi = (loanAmount * monthlyRate *
        Math.pow(1 + monthlyRate, numberOfMonths)) /
        (Math.pow(1 + monthlyRate, numberOfMonths) - 1);

    emiDisplay.textContent = '₹' + Math.round(emi).toLocaleString('en-IN');
}

document.getElementById('loan_amount').addEventListener('input', calculateEMI);
document.getElementById('interest_rate').addEventListener('input', calculateEMI);
document.getElementById('tenure').addEventListener('input', calculateEMI);
