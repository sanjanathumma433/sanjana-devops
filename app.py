from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-eligibility', methods=['POST'])
def check_eligibility():
    try:
        data = request.json
        
        # 1. AGE CHECK
        age = int(data.get('age', 0))
        if not (21 <= age <= 60):
            return jsonify({
                "status": "rejected",
                "reason": "Age must be between 21 and 60 years."
            })

        is_secured = data.get('is_secured') == 'Y'
        credit_score = int(data.get('credit_score', 0))

        # 2. SECURED LOAN LOGIC
        if is_secured:
            loan_amount = float(data.get('loan_amount', 0))
            collateral_value = float(data.get('collateral_value', 0))
            
            # Collateral check (Loan <= 70% of collateral)
            if loan_amount > (0.7 * collateral_value):
                return jsonify({
                    "status": "rejected",
                    "reason": "Loan amount exceeds 70% of collateral value."
                })
            
            # Credit Score check for secured
            if credit_score < 700:
                return jsonify({
                    "status": "rejected",
                    "reason": "Credit score too low for secured loan (Min: 700)."
                })
            
            return jsonify({
                "status": "approved",
                "message": "Loan Approved based on Collateral and Credit Score!",
                "details": {"type": "Secured"}
            })

        # 3. UNSECURED LOAN LOGIC
        else:
            employment = data.get('employment') # 1: Salaried, 2: Self-employed, 3: Govt, 4: Unemployed
            
            if employment == '4': # Unemployed
                return jsonify({"status": "rejected", "reason": "Applicant is currently unemployed."})

            # 3b. Self-employed Surety Check
            if employment == '2':
                has_surety = data.get('has_surety') == 'Y'
                if has_surety:
                    if credit_score >= 700:
                        return jsonify({"status": "approved", "message": "Loan Approved via Surety & Credit Score!"})
                    else:
                        return jsonify({"status": "rejected", "reason": "Credit score below 700 (required for surety-based approval)."})
                # If no surety, proceed to salary check (logic requirement)

            # 4. SALARY CHECK
            salary = float(data.get('salary', 0))
            if salary < 25000:
                return jsonify({"status": "rejected", "reason": "Minimum monthly salary must be ₹25,000."})

            # 5. EMI / DTI CHECK
            existing_emi = float(data.get('existing_emi', 0))
            eligible_emi_balance = (salary * 0.65) - existing_emi
            
            if eligible_emi_balance <= 2500:
                return jsonify({"status": "rejected", "reason": "Insufficient eligible EMI balance after existing commitments."})

            # 6. LOAN ELIGIBILITY CALCULATION
            p = float(data.get('loan_amount', 0))
            t_years = int(data.get('tenure', 0))
            annual_rate = float(data.get('interest_rate', 0))
            
            # Formula: EMI = [P x R x (1+R)^N]/[(1+R)^N-1]
            r = (annual_rate / 12) / 100 # monthly interest rate
            n = t_years * 12 # total months
            
            if r > 0:
                calculated_emi = (p * r * math.pow(1 + r, n)) / (math.pow(1 + r, n) - 1)
            else:
                calculated_emi = p / n

            if calculated_emi > eligible_emi_balance:
                return jsonify({
                    "status": "retry",
                    "reason": f"Requested EMI (₹{round(calculated_emi, 2)}) exceeds your eligible limit (₹{round(eligible_emi_balance, 2)}).",
                    "eligible_emi": round(eligible_emi_balance, 2),
                    "calculated_emi": round(calculated_emi, 2)
                })

            # 7. FINAL CREDIT SCORE CHECK
            if credit_score >= 700:
                return jsonify({
                    "status": "approved",
                    "message": "Loan Eligibility Confirmed!",
                    "details": {
                        "eligible_emi": round(eligible_emi_balance, 2),
                        "calculated_emi": round(calculated_emi, 2)
                    }
                })
            else:
                return jsonify({"status": "rejected", "reason": "Credit score must be 700 or higher for unsecured loans."})

    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)