import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import chi2_contingency
from scipy.stats import ttest_ind
from scipy.stats import mannwhitneyu
from scipy.stats import f_oneway
from scipy.stats import kruskal
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle, PageTemplate, BaseDocTemplate, Frame, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import pandas as pd
from scipy import stats
from scipy.stats import kruskal
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib import colors
import numpy as np
import random
from datetime import datetime
class reportgeneration:
    def __init__(self,real_data,synthetic_data):
        self.real_data=real_data
        self.synthetic_data=synthetic_data
        self.categorical_variables = real_data.select_dtypes(include=['object', 'category']).columns
        self.binary_variables = [col for col in real_data.columns if real_data[col].nunique() == 2]
        self.categorical_variables = list(set(self.categorical_variables) | set(self.binary_variables))
        self.continuous_variables = real_data.select_dtypes(include=['int64', 'float64']).columns
        self.continuous_variables = [col for col in self.continuous_variables if col not in self.binary_variables]
#         return self.create_pdf_report(output, self.real_data, self.synthetic_data, self.categorical_variables, self.continuous_variables, self.binary_variables)
    def generate_histogram_with_percentage(self,real_data, synthetic_data, variable_name, num_bins=10):
        combined_data = np.concatenate([real_data, synthetic_data])
        min_val, max_val = combined_data.min(), combined_data.max()
        bins = np.linspace(min_val, max_val, num=num_bins + 1)
        real_data_binned = np.digitize(real_data, bins=bins) - 1
        synthetic_data_binned = np.digitize(synthetic_data, bins=bins) - 1
        real_counts, _ = np.histogram(real_data, bins=bins)
        synthetic_counts, _ = np.histogram(synthetic_data, bins=bins)

        total_real = len(real_data)
        total_synthetic = len(synthetic_data)

        real_percentage = real_counts / total_real * 100
        synthetic_percentage = synthetic_counts / total_synthetic * 100
        labels = [f"{bins[i]:.2f}-{bins[i + 1]:.2f}" for i in range(len(bins) - 1)]
        bar_width = 0.35
        x = np.arange(len(labels))

        plt.figure(figsize=(8, 6))

        plt.bar(x - bar_width / 2, real_percentage, bar_width, alpha=0.5, label='Real Data')
        plt.bar(x + bar_width / 2, synthetic_percentage, bar_width, alpha=0.5, label='Synthetic Data')

        plt.xlabel(variable_name)
        plt.ylabel('Percentage')
        plt.title(f'{variable_name} Distribution Comparison')
        plt.xticks(x, labels, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()

        return img_buffer
    def plot_bar_for_categorical(self,real_data, synthetic_data, variable_name):
        real_percentage = (real_data.value_counts() / len(real_data)) * 100
        synthetic_percentage = (synthetic_data.value_counts() / len(synthetic_data)) * 100

        df = pd.DataFrame({'Real Data': real_percentage, 'Synthetic Data': synthetic_percentage}).fillna(0)

        plt.figure(figsize=(8, 5))
        df.plot(kind='bar', alpha=0.7)
        plt.xlabel(variable_name)
        plt.ylabel('Percentage')
        plt.title(f'{variable_name} Distribution Comparison')
        plt.legend()
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()

        return img_buffer
    def plot_bar_for_binary(self,real_data, synthetic_data, variable_name):
        real_percentage = (real_data.value_counts() / len(real_data)) * 100
        synthetic_percentage = (synthetic_data.value_counts() / len(synthetic_data)) * 100

        df = pd.DataFrame({'Real Data': real_percentage, 'Synthetic Data': synthetic_percentage}).fillna(0)

        plt.figure(figsize=(5, 3))
        df.plot(kind='bar', alpha=0.7)
        plt.xlabel(variable_name)
        plt.ylabel('Percentage')
        plt.title(f'{variable_name} Distribution Comparison')
        plt.legend()
        plt.tight_layout()

        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png')
        plt.close()

        return img_buffer
    def plot_pca_combined(self,real_data, synthetic_data, save_combined=None):
        data_numeric_real = real_data.select_dtypes(include='number')
        data_numeric_synthetic = synthetic_data.select_dtypes(include='number')

        imputer_real = SimpleImputer(strategy='mean')
        imputer_synthetic = SimpleImputer(strategy='mean')
        imputed_data_real = imputer_real.fit_transform(data_numeric_real)
        imputed_data_synthetic = imputer_synthetic.fit_transform(data_numeric_synthetic)

        scaler_real = StandardScaler()
        scaler_synthetic = StandardScaler()
        scaled_data_real = scaler_real.fit_transform(imputed_data_real)
        scaled_data_synthetic = scaler_synthetic.fit_transform(imputed_data_synthetic)

        pca_real = PCA(n_components=2)
        pca_synthetic = PCA(n_components=2)
        principal_components_real = pca_real.fit_transform(scaled_data_real)
        principal_components_synthetic = pca_synthetic.fit_transform(scaled_data_synthetic)

        pca_df_real = pd.DataFrame(data=principal_components_real, columns=['Principal Component 1', 'Principal Component 2'])
        pca_df_synthetic = pd.DataFrame(data=principal_components_synthetic, columns=['Principal Component 1', 'Principal Component 2'])
        pca_df_real['Dataset'] = 'Real Data'
        pca_df_synthetic['Dataset'] = 'Synthetic Data'

        plt.figure(figsize=(8, 6))
        plt.scatter(pca_df_real['Principal Component 1'], pca_df_real['Principal Component 2'],
                    c='b', label='Real Data', marker='o', alpha=0.7)
        plt.scatter(pca_df_synthetic['Principal Component 1'], pca_df_synthetic['Principal Component 2'],
                    c='r', label='Synthetic Data', marker='x', alpha=0.7)
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.title('PCA: Real vs. Synthetic Data')
        plt.legend()
        plt.tight_layout()

        if save_combined:
            plt.savefig(save_combined, format='png')
            plt.close()
    def print_bold_and_add_to_report(self,report, text):
        print(f"\033[1;4m{text}\033[0m")
        styles = getSampleStyleSheet()
        report.append(Paragraph(f"<b><font size='12'>{text}</font></b>", styles['Heading2']))

    def add_metadata(self,report, user_name, tool_used, execution_start_time, execution_end_time):
        styles = getSampleStyleSheet()
        metadata_text = f"<b>User Name:</b> {user_name}<br/><b>User ID:</b> {random.randint(10000, 99999)}<br/><b>Tool Used:</b> {tool_used}<br/><b>Execution Start Time:</b> {execution_start_time}<br/><b>Execution End Time:</b> {execution_end_time}"
        report.append(Spacer(1, 0.01 * inch))
        report.append(Paragraph(metadata_text, styles['Normal']))
        report.append(HRFlowable(width="100%", thickness=1, lineCap='round', color='black', spaceBefore=0.2 * inch, spaceAfter=0.2 * inch))

        report.append(Spacer(1, 0.01 * inch))

    def add_table(self,report, styles, heading, data, columns):
        report.append(Spacer(1, 12))
        report.append(Paragraph(f"<b><font size='14'>{heading}</font></b>", styles['Heading2']))
        report.append(Spacer(1, 12))
        max_width = 540
        col_widths = (max_width - 100) // (len(columns) + 1)
        table_style = [('GRID', (0, 0), (-1, -1), 1, 'black'),
                       ('COLWIDTH', (0, 0), (-1, -1), col_widths)]
        table_data = [columns + ['Result']] 
        for row in data:
            result = "Pass" if "closely matches" in row[3] or "similar" in row[3] or "Similar" in row[3] else "Fail"
            modified_row = [cell if not isinstance(cell, str) or len(cell) < 30 else Paragraph(cell, styles['Normal']) for cell in row]
            modified_row.append(result)
            table_data.append(modified_row)
        table = Table(table_data, style=table_style, hAlign='LEFT')
        report.append(table)
        report.append(Spacer(1, 12))

    def create_pdf_report(self,output_filename,user_name,tool_used):
        real_data=self.real_data
        synthetic_data=self.synthetic_data
        categorical_variables=self.categorical_variables
        continuous_variables=self.continuous_variables 
        binary_variables=self.binary_variables
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        report = []
        styles = getSampleStyleSheet()

        def add_paragraph(text):
            report.append(Paragraph(text, styles['Normal']))
            report.append(Spacer(1, 12)) 
#         user_name = input("Enter User Name: ")
#         user_name="Aaryan"
# #         tool_used = input("Enter the Tool Used for Synthetic Data Generation: ")
#         tool_used="Gretel"
        execution_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        execution_end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.add_metadata(report, user_name, tool_used, execution_start_time, execution_end_time)


        self.print_bold_and_add_to_report(report, "All Categorical Variables:")
        for col in categorical_variables:
            add_paragraph(col)

        self.print_bold_and_add_to_report(report, "Independent Continuous Variables:")
        for col in continuous_variables:
            add_paragraph(col)

        report.append(PageBreak())

        real_continuous = real_data[continuous_variables]
        synthetic_continuous = synthetic_data[continuous_variables]

        ks_test_results = []
        t_test_results = []
        mwu_test_results = []
        anova_test_results = []
        kruskal_test_results = []

        for col in continuous_variables:
            # Kolmogorov-Smirnov Test
            ks_statistic, ks_p_value = stats.ks_2samp(real_continuous[col], synthetic_continuous[col])
            ks_inference = "Closely matches the real data distribution i.e. similar." if ks_p_value > 0.05 else "Does not match the real data distribution significantly."

            # T-Test
            t_statistic, t_p_value = stats.ttest_ind(real_continuous[col], synthetic_continuous[col])
            t_inference = "Similar means as real data." if t_p_value > 0.05 else "Significantly different means from real data."

            # Mann-Whitney U Test
            mwu_statistic, mwu_p_value = stats.mannwhitneyu(real_continuous[col], synthetic_continuous[col])
            mwu_inference = "Similar distributions as real data." if mwu_p_value > 0.05 else "Significantly different distributions from real data."

            # ANOVA Test
            f_statistic, p_value = stats.f_oneway(real_data[col].dropna(), synthetic_data[col].dropna())
            anova_inference = "Similar means as real data." if p_value > 0.05 else "Significantly different means from real data."

            # Kruskal-Wallis Test
            h_statistic, p_value = kruskal(real_data[col].dropna(), synthetic_data[col].dropna())
            kruskal_inference = "Similar distributions as real data." if p_value > 0.05 else "Significantly different distributions from real data."

            ks_test_results.append([col, ks_p_value, ks_statistic, ks_inference])
            t_test_results.append([col, t_p_value, t_statistic, t_inference])
            mwu_test_results.append([col, mwu_p_value, mwu_statistic, mwu_inference])
            anova_test_results.append([col, p_value, f_statistic, anova_inference])
            kruskal_test_results.append([col, p_value, h_statistic, kruskal_inference])

        # Chi-Square test
        chi2_test_results = []
        for col in categorical_variables:
            cross_tab = pd.crosstab(real_data[col], synthetic_data[col])
            chi2_statistic, chi2_p_value, _, _ = stats.chi2_contingency(cross_tab)
            chi2_inference = "Sig. association between the two variables (similar)" if chi2_p_value > 0.05 else "No association between the two variables."
            chi2_test_results.append([col, chi2_p_value, chi2_statistic, chi2_inference])

        test_results = [
            ("Kolmogorov-Smirnov Test Results:", ks_test_results, ["Variable", "p-value", "KS-Statistic", "Inference"]),
            ("T-Test Results:", t_test_results, ["Variable", "p-value", "T-Statistic", "Inference"]),
            ("Mann-Whitney U Test Results:", mwu_test_results, ["Variable", "p-value", "MWU-Statistic", "Inference"]),
            ("ANOVA Results:", anova_test_results, ["Variable", "p-value", "F-Statistic", "Inference"]),
            ("Kruskal-Wallis Test Results:", kruskal_test_results, ["Variable", "p-value", "H-Statistic", "Inference"]),
            ("Chi-Square Test Results:", chi2_test_results, ["Variable", "p-value", "Chi2 Statistic", "Inference"])
        ]

        for heading, data, columns in test_results:
            self.add_metadata(report, user_name, tool_used, execution_start_time, execution_end_time)
            self.add_table(report, styles, heading, data, columns)
            report.append(PageBreak())


        for col in continuous_variables:
            self.add_metadata(report, user_name, tool_used, execution_start_time, execution_end_time)
            img_buffer = self.generate_histogram_with_percentage(real_data[col].dropna(), synthetic_data[col].dropna(), col)
            img = Image(img_buffer)
            report.append(img)
            report.append(PageBreak())

        for col in categorical_variables:
            unique_categories = len(real_data[col].unique())
            if 2 < unique_categories < 10:
                self.add_metadata(report, user_name, tool_used, execution_start_time, execution_end_time)
                img_buffer = self.plot_bar_for_categorical(real_data[col], synthetic_data[col], col)
                img = Image(img_buffer)
                report.append(img)
                report.append(PageBreak()) 
        for col in binary_variables:
            self.add_metadata(report, user_name, tool_used, execution_start_time, execution_end_time)
            img_buffer = self.plot_bar_for_binary(real_data[col], synthetic_data[col], col)
            img = Image(img_buffer)
            report.append(img)
            report.append(PageBreak()) 

        img_buffer_combined = BytesIO()
        self.add_metadata(report, user_name, tool_used, execution_start_time, execution_end_time)
        self.plot_pca_combined(real_data, synthetic_data, save_combined=img_buffer_combined)

        img_combined = Image(img_buffer_combined)

        report.append(Paragraph("<b><font size='14'>PCA: Real vs. Synthetic Data</font></b>", styles['Heading2']))
        report.append(img_combined)

        doc.build(report)
#         return(report)


