import os
import yaml
import pandas as pd

# Paths
licenses_path = "choosealicense.com/_licenses"
rules_path = "choosealicense.com/_data/rules.yml"
output_csv = "licenses_data.csv"

# Load rules
with open(rules_path, "r", encoding="utf-8") as file:
    rules = yaml.safe_load(file)

# Extract rule tags with categories
all_tags = {}
for category, rule_list in rules.items():
    for rule in rule_list:
        all_tags[rule["tag"]] = (rule["label"], category)
columns = list(set(label for label, _ in all_tags.values()))

# List to store extracted data
licenses_data = []

# Read all .txt files in the directory
for filename in os.listdir(licenses_path):
    if filename.endswith(".txt"):
        with open(os.path.join(licenses_path, filename), "r", encoding="utf-8") as file:
            content = file.read()

            # Extract YAML front matter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) > 2:
                    yaml_content = parts[1]
                    try:
                        data = yaml.safe_load(yaml_content)
                        row = {label: "" for label in columns}
                        row["Title"] = data.get("title", "Unknown")
                        row["SPDX-ID"] = data.get("spdx-id", "Unknown")
                        row["URL"] = "https://choosealicense.com/licenses/" + row["SPDX-ID"].lower()
                        for category in ["permissions", "conditions", "limitations"]:
                            for tag in data.get(category, []):
                                if tag in all_tags:
                                    label, cat = all_tags[tag]
                                    row[label] = cat.capitalize()
                        licenses_data.append(row)
                    except yaml.YAMLError as e:
                        print(f"Error parsing {filename}: {e}")

# Convert to DataFrame
df = pd.DataFrame(licenses_data)

# Reorder columns to have Title and SPDX-ID first
column_order = ["Title", "SPDX-ID", "URL"] + [col for col in df.columns if col not in ["Title", "SPDX-ID"]]
df = df[column_order]

# Save DataFrame to CSV
df.to_csv(output_csv, index=False)
