import json
from marshmallow import Schema, fields, post_load

with open("merged_subsidy_applications.json", "r") as file:
    data = json.load(file)

n = 1
data_cleaned = []

class Application:
    def __init__(self, obj):
        self.id = 0
        self.application_id = obj.get("application_id", "")
        self.name = obj.get("applicant_name", "")
        self.household_income = obj.get("household_income", 0)
        self.employment_status = obj.get("employment_status", "")
        self.num_children = obj.get("num_children", 0)
        self.child_ages = obj.get("child_ages", [])
        self.childcare_hours_requested = obj.get("childcare_hours_requested", 0)
        if self.childcare_hours_requested == 0:
            self.childcare_hours_requested = obj.get("requested_hours", 0)
        self.housing_situation = obj.get("housing_situation", "")
        self.partner_employed = obj.get("partner_employed", False)
        self.recent_municipal_support = obj.get("recent_municipal_support", [])
        self.flags = obj.get("flags", {})
        self.eligibility = True
        self.encoded_num_children = 0
        self.vulnerability = False
        self.prompt = ""
        self.decision = ""
        self.reason = ""

    def correct_num_children(self):
        if self.num_children <= 0:
            self.eligibility = False
        for age in self.child_ages:
            if age < 12 :
                if self.encoded_num_children < 2:
                    self.encoded_num_children += 1
            if self.encoded_num_children == 2:
                break   
        if self.encoded_num_children == 0:
            self.eligibility = False 
            
    def correct_work_status(self):
        if self.employment_status == "unemployed" and not self.partner_employed:
            self.eligibility = False
                
    def correct_income(self):
        if self.household_income < 0:
            self.eligibility = False
        elif self.household_income > 50000:
            self.eligibility = False
    
    def correct_vulnerability(self):
        if self.housing_situation == "unstable" or self.recent_municipal_support:
            self.vulnerability = True

    
for item in data:   
    data_cleaned.append(Application(item))
    data_cleaned[-1].id = n
    n += 1
    data_cleaned[-1].correct_num_children()
    data_cleaned[-1].correct_work_status()
    data_cleaned[-1].correct_income()
    data_cleaned[-1].correct_vulnerability()
    
# for item in data_cleaned:
#     print(f"ID: {item.id}, Application ID: {item.application_id}, Name: {item.name}, "
#           f"Income: {item.household_income}, Employment Status: {item.employment_status}, "
#           f"Children: {item.num_children}, Child Ages: {item.child_ages}, "
#           f"Childcare Hours Requested: {item.childcare_hours_requested}, "
#           f"Housing Situation: {item.housing_situation}, Partner Employed: {item.partner_employed}, "
#           f"Recent Municipal Support: {item.recent_municipal_support}, Flags: {item.flags}")
#     break

# class ApplicationEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Application):
#             return {
#                 "id": obj.id,
#                 "application_id": obj.application_id,
#                 "name": obj.name,
#                 "household_income": obj.household_income,
#                 "employment_status": obj.employment_status,
#                 "num_children": obj.num_children,
#                 "child_ages": obj.child_ages,
#                 "childcare_hours_requested": obj.childcare_hours_requested,
#                 "housing_situation": obj.housing_situation,
#                 "partner_employed": obj.partner_employed,
#                 "recent_municipal_support": obj.recent_municipal_support,
#                 "flags": obj.flags
#             }
#         return super().default(obj)
    
class ApplicationEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Application):
            if not obj.eligibility:
                pass
            return {
                "id": obj.id,
                "application_id": "XXXXX",
                "name": "XXXXX",
                "household_income": obj.household_income,
                "employment_status": obj.employment_status,
                "num_children": obj.encoded_num_children,
                "child_ages": obj.child_ages,
                "childcare_hours_requested": obj.childcare_hours_requested,
                "housing_situation": obj.housing_situation,
                "partner_employed": obj.partner_employed,
                "recent_municipal_support": obj.recent_municipal_support,
                "flags": obj.flags
                
            }
        return super().default(obj)
    
print("Saving cleaned data to 'cleaned_subsidy_applications.json'...")
with open("cleaned_subsidy_applications.json", "w") as file:
    json.dump(data_cleaned, file, cls=ApplicationEncoder, indent=4)
    
print("Data cleaning complete. Cleaned data saved to 'cleaned_subsidy_applications.json'.")
print("Total applications processed:", len(data_cleaned))

list_of_elligibles = []

for item in data_cleaned:
    if item.eligibility:
        temp = f"The applicant named XXXX has household income {item.household_income}. The applicant requested for {item.childcare_hours_requested} childcare hours subsidy."
        temp += f"The housing situation is {item.housing_situation}. "
        if item.partner_employed:
            temp += "The partner is also employed. "
        if item.recent_municipal_support:
            temp += f"Recent municipal support includes for that person is listed: {', '.join(item.recent_municipal_support)}. "
        if item.flags.get("incomplete_docs", True):
            temp += "The application has incomplete documents. "
        if item.flags.get("income_mismatch", False):
            temp += "There is an income mismatch. "
        
        list_of_elligibles.append((item.id, temp))
        item.prompt = temp
        
print("List of eligible applications:")
for id, description in list_of_elligibles:
    print(f"ID: {id}, Description: {description}")

# Save the list of eligible applications to a file
with open("eligible_applications.txt", "w") as file:
    for id, description in list_of_elligibles:
        file.write(f"ID: {id}, Description: {description}\n")
print("Eligible applications saved to 'eligible_applications.txt'.")


import re

output = """Agent step (convert json to English):
This JSON object contains information about an application, which has the following structure:

* The application has a unique identifier, referred to as the "application_id", which is set to "A001".
* The applicant's name is stored in the "applicant_name" field, and it is "Laura Visser".
* The "household_income" field contains the total income of the household, which is 63506.
* The "employment_status" field indicates the current employment status of the applicant, which is "unemployed".
* The "num_children" field specifies the number of children in the household, which is 1.
* The "child_ages" field is an array that contains the ages of the children, and in this case, it has one item: 3, indicating that there is one child who is 3 years old.
* The "childcare_hours_requested" field represents the number of childcare hours requested by the applicant, which is 137.
* The "housing_situation" field describes the current housing situation of the applicant, which is "municipal housing".
* The "partner_employed" field indicates whether the applicant's partner is employed, and it is set to true, meaning the partner is employed.
* The "recent_municipal_support" field is an array that lists the types of support the applicant has recently received from the municipality, and it contains one item: "food aid", indicating that the applicant has received food aid.
* The "flags" field is an object that contains several flags or indicators related to the application. It has the following nested fields:
  - "incomplete_docs" is a flag that indicates whether the application has incomplete documents, and it is set to true.
  - "high_hours_request" is a flag that indicates whether the requested childcare hours are high, and it is set to true.
  - "income_mismatch" is a flag that indicates whether there is a mismatch in the reported income, and it is set to false, meaning there is no income mismatch.

Overall, this JSON object provides a comprehensive overview of the application, including the applicant's personal and financial information, their household situation, and any relevant flags or indicators.
---
Agent step (analyze regulations):
I'll go through each rule and indicate whether it appears to be relevant to any part of the application summary.

## Article 1. General Provisions

* **1.1 Purpose**: No matching information in the application.
* **1.2 Definitions**: 
  - **Applicant**: Relevant, as the application includes information about the applicant, such as their name and employment status.
  - **Minor**: Relevant, as the application mentions a 3-year-old child.
  - **Eligible Care**: No matching information in the application.
  - **Subsidy**: No matching information in the application.
  - **Means-tested Assessment**: Relevant, as the application includes household income information.

## Article 2. Eligibility Criteria

* **2.1 Citizenship and Residency**: No matching information in the application.
* **2.2 Employment or Education Status**: Relevant, as the application mentions the applicant's employment status (unemployed) and their partner's employment status (employed).
* **2.3 Income Threshold**: Relevant, as the application includes household income information (63506).
* **2.4 Vulnerability Clause**: Relevant, as the application mentions that the applicant has received food aid and lives in municipal housing.

## Article 3. Application Procedure

* **3.1 Submission Requirements**: No matching information in the application.
* **3.2 Submission Window**: No matching information in the application.
* **3.3 Digital Filing**: No matching information in the application.

## Article 4. Subsidy Calculation and Disbursement

* **4.1 Reimbursement Ceiling**: Relevant, as the application includes household income information (63506) and childcare hours requested (137).
* **4.2 Child Cap**: Relevant, as the application mentions one child.
* **4.3 Disbursement Frequency**: No matching information in the application.

## Article 5. Income Verification and Audits

* **5.1 Means-Tested Review**: Relevant, as the application includes household income information (63506).
* **5.2 Documentation Audit**: Relevant, as the application has a flag indicating incomplete documents.
* **5.3 Automated Risk Flagging**: Relevant, as the application has several flags, including "incomplete_docs" and "high_hours_request".

## Article 6. Appeals and Human Oversight

* **6.1 Right to Appeal**: No matching information in the application.
* **6.2 Review Committee**: No matching information in the application.
* **6.3 Agent-Based Decision Transparency**: No matching information in the application.

## Article 7. Final Provisions

* **7.1 Entry into Force**: No matching information in the application.
* **7.2 Repeals**: No matching information in the application.
* **7.3 Review Clause**: No matching information in the application.
---
Agent step (make decision):
Decision: HUMAN REVIEW  
Reason: The application has incomplete documents, as indicated by the "incomplete_docs" flag, which requires further review to ensure all necessary information is provided before making a decision.
---
Agent step (Stop):
{
  "kind": "final_step",
  "reason": ""
}
---
Agent final answer: Decision: HUMAN REVIEW REQUIRED
Reason: The application has incomplete documents, as indicated by the "incomplete_docs" flag, which requires further review to ensure all necessary information is provided before making a decision."""

# Extracting decision and reason
match = re.search(r'Agent final answer: Decision:\s*(.+?)\s*Reason:\s*(.+)', output, re.DOTALL)

if match:
    decision = match.group(1).strip()
    reason = match.group(2).strip()
    print("Decision:", decision)
    print("Reason:", reason)
else:
    print("Could not parse output.")

from tabulate import tabulate

def tabulate_result(self) -> str:
    data = [
        ["Application ID", self.application_id],
        ["Applicant Name", self.name],
        ["Household Income", self.household_income],
        ["Employment Status", self.employment_status],
        ["Number of Children", self.num_children],
        ["Child Ages", ", ".join(map(str, self.child_ages)) if self.child_ages else "None"],
        ["Childcare Hours Requested", self.childcare_hours_requested],
        ["Housing Situation", self.housing_situation],
        ["Partner Employed", "Yes" if self.partner_employed else "No"],
        ["Recent Municipal Support", ", ".join(self.recent_municipal_support) if self.recent_municipal_support else "None"],
        ["Decision", self.decision],
        ["Reason", self.reason],
    ]
    
    return tabulate(data, headers=["Field", "Value"], tablefmt="grid")

print(tabulate_result(data_cleaned[0], decision, reason))

with open("application_summary.txt", "w") as file:
    file.write(tabulate_result(data_cleaned[0], decision, reason))