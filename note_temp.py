import json
from datetime import datetime

note_templates = {
    "10": {
        "title": "Long Term Loans and Advances",
        "full_title": "10. Long Term Loans and Advances",
        "structure": [
            {
                "category": "In Lakhs",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Unsecured, considered good",
                "subcategories": [
                    {
                        "label": "Long Term - Security Deposits",
                        "value": "{security_deposits_2024}",
                        "previous_value": "{security_deposits_2023}"
                    }
                ],
                "total": "{unsecured_total_2024}",
                "previous_total": "{unsecured_total_2023}"
            }
        ],
        "metadata": {
            "note_number": "10",
            "generated_on": "{generated_on}"
        }
    },
    "11": {
        "title": "Inventories",
        "full_title": "11. Inventories",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Consumables",
                "subcategories": [],
                "total": "{consumables_2024}",
                "previous_total": "{consumables_2023}"
            }
        ],
        "metadata": {
            "note_number": "11",
            "generated_on": "{generated_on}"
        }
    },
    "12": {
        "title": "Trade Receivables",
        "full_title": "12. Trade Receivables",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Unsecured, considered good",
                "subcategories": [
                    {
                        "label": "Outstanding for a period exceeding six months from the date they are due for payment",
                        "value": "{over_six_months_2024}",
                        "previous_value": "{over_six_months_2023}"
                    },
                    {
                        "label": "Other receivables",
                        "value": "{other_receivables_2024}",
                        "previous_value": "{other_receivables_2023}"
                    }
                ],
                "total": "{unsecured_total_2024}",
                "previous_total": "{unsecured_total_2023}"
            },
            {
                "category": "Age wise analysis of Trade receivables as on 31.03.2024",
                "subcategories": [
                    {
                        "label": "Particulars",
                        "sub_label": "Outstanding for following periods from due date of payment",
                        "columns": [
                            {"header": "0 - 6 months", "value": "{zero_six_2024}"},
                            {"header": "6 months - 1 Year", "value": "{six_one_2024}"},
                            {"header": "1 - 2 Years", "value": "{one_two_2024}"},
                            {"header": "2 - 3 Years", "value": "{two_three_2024}"},
                            {"header": "More than 3 Years", "value": "{more_three_2024}"},
                            {"header": "Total", "value": "{age_total_2024}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_good_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_good_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_good_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_good_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{undisputed_good_more_three_2024}"},
                            {"period": "Total", "value": "{undisputed_good_total_2024}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_doubtful_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_doubtful_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_doubtful_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_doubtful_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{undisputed_doubtful_more_three_2024}"},
                            {"period": "Total", "value": "{undisputed_doubtful_total_2024}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_good_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_good_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{disputed_good_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{disputed_good_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{disputed_good_more_three_2024}"},
                            {"period": "Total", "value": "{disputed_good_total_2024}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_doubtful_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_doubtful_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{disputed_doubtful_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{disputed_doubtful_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{disputed_doubtful_more_three_2024}"},
                            {"period": "Total", "value": "{disputed_doubtful_total_2024}"}
                        ]
                    },
                    {
                        "label": "Total",
                        "values": [
                            {"period": "0 - 6 months", "value": "{total_zero_six_2024}"},
                            {"period": "6 months - 1 Year", "value": "{total_six_one_2024}"},
                            {"period": "1 - 2 Years", "value": "{total_one_two_2024}"},
                            {"period": "2 - 3 Years", "value": "{total_two_three_2024}"},
                            {"period": "More than 3 Years", "value": "{total_more_three_2024}"},
                            {"period": "Total", "value": "{age_total_2024}"}
                        ]
                    }
                ]
            },
            {
                "category": "Age wise analysis of Trade receivables as on 31.03.2023",
                "subcategories": [
                    {
                        "label": "Particulars",
                        "sub_label": "Outstanding for following periods from due date of payment",
                        "columns": [
                            {"header": "0 - 6 months", "value": "{zero_six_2023}"},
                            {"header": "6 months - 1 Year", "value": "{six_one_2023}"},
                            {"header": "1 - 2 Years", "value": "{one_two_2023}"},
                            {"header": "2 - 3 Years", "value": "{two_three_2023}"},
                            {"header": "More than 3 Years", "value": "{more_three_2023}"},
                            {"header": "Total", "value": "{age_total_2023}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_good_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_good_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_good_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_good_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{undisputed_good_more_three_2023}"},
                            {"period": "Total", "value": "{undisputed_good_total_2023}"}
                        ]
                    },
                    {
                        "label": "Undisputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{undisputed_doubtful_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{undisputed_doubtful_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{undisputed_doubtful_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{undisputed_doubtful_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{undisputed_doubtful_more_three_2023}"},
                            {"period": "Total", "value": "{undisputed_doubtful_total_2023}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered good",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_good_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_good_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{disputed_good_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{disputed_good_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{disputed_good_more_three_2023}"},
                            {"period": "Total", "value": "{disputed_good_total_2023}"}
                        ]
                    },
                    {
                        "label": "Disputed",
                        "sub_label": "- Considered doubtful",
                        "values": [
                            {"period": "0 - 6 months", "value": "{disputed_doubtful_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{disputed_doubtful_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{disputed_doubtful_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{disputed_doubtful_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{disputed_doubtful_more_three_2023}"},
                            {"period": "Total", "value": "{disputed_doubtful_total_2023}"}
                        ]
                    },
                    {
                        "label": "Total",
                        "values": [
                            {"period": "0 - 6 months", "value": "{total_zero_six_2023}"},
                            {"period": "6 months - 1 Year", "value": "{total_six_one_2023}"},
                            {"period": "1 - 2 Years", "value": "{total_one_two_2023}"},
                            {"period": "2 - 3 Years", "value": "{total_two_three_2023}"},
                            {"period": "More than 3 Years", "value": "{total_more_three_2023}"},
                            {"period": "Total", "value": "{age_total_2023}"}
                        ]
                    }
                ]
            }
        ],
        "metadata": {
            "note_number": "12",
            "generated_on": "{generated_on}"
        }
    },
    "13": {
        "title": "Cash and Bank Balances",
        "full_title": "13. Cash and Bank Balances",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Cash and cash equivalents",
                "subcategories": [
                    {
                        "label": "Balances with banks in current accounts",
                        "value": "{bank_balances_2024}",
                        "previous_value": "{bank_balances_2023}"
                    },
                    {
                        "label": "Cash on hand",
                        "value": "{cash_on_hand_2024}",
                        "previous_value": "{cash_on_hand_2023}"
                    }
                ]
            },
            {
                "category": "Other Bank Balances",
                "subcategories": [
                    {
                        "label": "Fixed Deposits with ICICI Bank",
                        "value": "{fixed_deposits_2024}",
                        "previous_value": "{fixed_deposits_2023}"
                    }
                ]
            },
            {
                "category": "Total",
                "subcategories": [],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "13",
            "generated_on": "{generated_on}"
        }
    },
    "14": {
        "title": "Short Term Loans and Advances",
        "full_title": "14. Short Term Loans and Advances",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Unsecured, considered good",
                "subcategories": [
                    {
                        "label": "Prepaid Expenses",
                        "value": "{prepaid_expenses_2024}",
                        "previous_value": "{prepaid_expenses_2023}"
                    },
                    {
                        "label": "Other Advances",
                        "value": "{other_advances_2024}",
                        "previous_value": "{other_advances_2023}"
                    }
                ]
            },
            {
                "category": "Other loans and advances",
                "subcategories": [
                    {
                        "label": "Advance tax",
                        "value": "{advance_tax_2024}",
                        "previous_value": "{advance_tax_2023}"
                    },
                    {
                        "label": "Balances with statutory/government authorities",
                        "value": "{statutory_balances_2024}",
                        "previous_value": "{statutory_balances_2023}"
                    }
                ]
            },
            {
                "category": "Total",
                "subcategories": [],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "14",
            "generated_on": "{generated_on}"
        }
    },
    "15": {
        "title": "Other Current Assets",
        "full_title": "15. Other Current Assets",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Interest accrued on fixed deposits",
                "subcategories": [],
                "total": "{interest_accrued_2024}",
                "previous_total": "{interest_accrued_2023}"
            }
        ],
        "metadata": {
            "note_number": "15",
            "generated_on": "{generated_on}"
        }
    },
    "16": {
        "title": "Revenue from Operations",
        "full_title": "16. Revenue from Operations",
        "structure": [
            {
                "category": "In Lakhs",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Sale of Services",
                "subcategories": [
                    {
                        "label": "Domestic",
                        "value": "{domestic_2024}",
                        "previous_value": "{domestic_2023}"
                    },
                    {
                        "label": "Exports",
                        "value": "{exports_2024}",
                        "previous_value": "{exports_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "16",
            "generated_on": "{generated_on}"
        }
    },
    "17": {
        "title": "Other Income",
        "full_title": "17. Other Income",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "Interest income",
                        "value": "{interest_income_2024}",
                        "previous_value": "{interest_income_2023}"
                    },
                    {
                        "label": "Foreign exchange gain (Net)",
                        "value": "{foreign_exchange_gain_2024}",
                        "previous_value": "{foreign_exchange_gain_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "17",
            "generated_on": "{generated_on}"
        }
    },
    "18": {
        "title": "Cost of Materials Consumed",
        "full_title": "18. Cost of Materials Consumed",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "Opening Stock",
                        "value": "{opening_stock_2024}",
                        "previous_value": "{opening_stock_2023}"
                    },
                    {
                        "label": "Add: Purchases",
                        "value": "{purchases_2024}",
                        "previous_value": "{purchases_2023}"
                    },
                    {
                        "label": "",
                        "value": "{subtotal_2024}",
                        "previous_value": "{subtotal_2023}"
                    },
                    {
                        "label": "Less: Closing Stock",
                        "value": "{closing_stock_2024}",
                        "previous_value": "{closing_stock_2023}"
                    }
                ],
                "total": "{cost_materials_consumed_2024}",
                "previous_total": "{cost_materials_consumed_2023}"
            }
        ],
        "metadata": {
            "note_number": "18",
            "generated_on": "{generated_on}"
        }
    },
    "19": {
        "title": "Employee Benefit Expense",
        "full_title": "19. Employee Benefit Expense",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "Salaries, wages and bonus",
                        "value": "{salaries_wages_bonus_2024}",
                        "previous_value": "{salaries_wages_bonus_2023}"
                    },
                    {
                        "label": "Contribution to PF & ESI",
                        "value": "{contribution_pf_esi_2024}",
                        "previous_value": "{contribution_pf_esi_2023}"
                    },
                    {
                        "label": "Staff welfare expenses",
                        "value": "{staff_welfare_expenses_2024}",
                        "previous_value": "{staff_welfare_expenses_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "19",
            "generated_on": "{generated_on}"
        }
    },
    "20": {
        "title": "Other Expenses",
        "full_title": "20. Other Expenses",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "BA / BE NOC Charges",
                        "value": "{ba_be_noc_charges_2024}",
                        "previous_value": "{ba_be_noc_charges_2023}"
                    },
                    {
                        "label": "BA Expenses",
                        "value": "{ba_expenses_2024}",
                        "previous_value": "{ba_expenses_2023}"
                    },
                    {
                        "label": "Payments to Volunteers",
                        "value": "{payments_to_volunteers_2024}",
                        "previous_value": "{payments_to_volunteers_2023}"
                    },
                    {
                        "label": "Other Operating Expenses",
                        "value": "{other_operating_expenses_2024}",
                        "previous_value": "{other_operating_expenses_2023}"
                    },
                    {
                        "label": "Laboratory testing charges",
                        "value": "{laboratory_testing_charges_2024}",
                        "previous_value": "{laboratory_testing_charges_2023}"
                    },
                    {
                        "label": "Rent",
                        "value": "{rent_2024}",
                        "previous_value": "{rent_2023}"
                    },
                    {
                        "label": "Rates & Taxes",
                        "value": "{rates_taxes_2024}",
                        "previous_value": "{rates_taxes_2023}"
                    },
                    {
                        "label": "Fees & licenses",
                        "value": "{fees_licenses_2024}",
                        "previous_value": "{fees_licenses_2023}"
                    },
                    {
                        "label": "Insurance",
                        "value": "{insurance_2024}",
                        "previous_value": "{insurance_2023}"
                    },
                    {
                        "label": "Membership & Subscription Charges",
                        "value": "{membership_subscription_charges_2024}",
                        "previous_value": "{membership_subscription_charges_2023}"
                    },
                    {
                        "label": "Postage & Communication Cost",
                        "value": "{postage_communication_cost_2024}",
                        "previous_value": "{postage_communication_cost_2023}"
                    },
                    {
                        "label": "Printing and stationery",
                        "value": "{printing_stationery_2024}",
                        "previous_value": "{printing_stationery_2023}"
                    },
                    {
                        "label": "CSR Fund Expenses",
                        "value": "{csr_fund_expenses_2024}",
                        "previous_value": "{csr_fund_expenses_2023}"
                    },
                    {
                        "label": "Telephone & Internet",
                        "value": "{telephone_internet_2024}",
                        "previous_value": "{telephone_internet_2023}"
                    },
                    {
                        "label": "Travelling and Conveyance",
                        "value": "{travelling_conveyance_2024}",
                        "previous_value": "{travelling_conveyance_2023}"
                    },
                    {
                        "label": "Translation Charges",
                        "value": "{translation_charges_2024}",
                        "previous_value": "{translation_charges_2023}"
                    },
                    {
                        "label": "Electricity Charges",
                        "value": "{electricity_charges_2024}",
                        "previous_value": "{electricity_charges_2023}"
                    },
                    {
                        "label": "Security Charges",
                        "value": "{security_charges_2024}",
                        "previous_value": "{security_charges_2023}"
                    },
                    {
                        "label": "Annual Maintenance Charges",
                        "value": "{annual_maintenance_charges_2024}",
                        "previous_value": "{annual_maintenance_charges_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Electrical",
                        "value": "{repairs_maintenance_electrical_2024}",
                        "previous_value": "{repairs_maintenance_electrical_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Office",
                        "value": "{repairs_maintenance_office_2024}",
                        "previous_value": "{repairs_maintenance_office_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Machinery",
                        "value": "{repairs_maintenance_machinery_2024}",
                        "previous_value": "{repairs_maintenance_machinery_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Vehicles",
                        "value": "{repairs_maintenance_vehicles_2024}",
                        "previous_value": "{repairs_maintenance_vehicles_2023}"
                    },
                    {
                        "label": "Repairs and maintenance - Others",
                        "value": "{repairs_maintenance_others_2024}",
                        "previous_value": "{repairs_maintenance_others_2023}"
                    },
                    {
                        "label": "Business Development Expenses",
                        "value": "{business_development_expenses_2024}",
                        "previous_value": "{business_development_expenses_2023}"
                    },
                    {
                        "label": "Professional & Consultancy Fees",
                        "value": "{professional_consultancy_fees_2024}",
                        "previous_value": "{professional_consultancy_fees_2023}"
                    },
                    {
                        "label": "Payment to Auditors",
                        "value": "{payment_to_auditors_2024}",
                        "previous_value": "{payment_to_auditors_2023}"
                    },
                    {
                        "label": "Bad Debts Written Off",
                        "value": "{bad_debts_written_off_2024}",
                        "previous_value": "{bad_debts_written_off_2023}"
                    },
                    {
                        "label": "Fire Extinguishers Refilling Charges",
                        "value": "{fire_extinguishers_refilling_charges_2024}",
                        "previous_value": "{fire_extinguishers_refilling_charges_2023}"
                    },
                    {
                        "label": "Food Expenses for Guests",
                        "value": "{food_expenses_for_guests_2024}",
                        "previous_value": "{food_expenses_for_guests_2023}"
                    },
                    {
                        "label": "Diesel Expenses",
                        "value": "{diesel_expenses_2024}",
                        "previous_value": "{diesel_expenses_2023}"
                    },
                    {
                        "label": "Interest Under 234 C Fy 2021-22",
                        "value": "{interest_under_234c_2024}",
                        "previous_value": "{interest_under_234c_2023}"
                    },
                    {
                        "label": "Loan Processing Charges",
                        "value": "{loan_processing_charges_2024}",
                        "previous_value": "{loan_processing_charges_2023}"
                    },
                    {
                        "label": "Sitting Fee of Directors",
                        "value": "{sitting_fee_directors_2024}",
                        "previous_value": "{sitting_fee_directors_2023}"
                    },
                    {
                        "label": "Customs Duty Payment",
                        "value": "{customs_duty_payment_2024}",
                        "previous_value": "{customs_duty_payment_2023}"
                    },
                    {
                        "label": "Transportation and Unloading Charges",
                        "value": "{transportation_unloading_charges_2024}",
                        "previous_value": "{transportation_unloading_charges_2023}"
                    },
                    {
                        "label": "Software Equipment",
                        "value": "{software_equipment_2024}",
                        "previous_value": "{software_equipment_2023}"
                    },
                    {
                        "label": "Miscellaneous expenses",
                        "value": "{miscellaneous_expenses_2024}",
                        "previous_value": "{miscellaneous_expenses_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "20",
            "generated_on": "{generated_on}"
        },
        "notes_and_disclosures": [
            "* Fees is net of GST which is taken as input tax credit."
        ]
    },
    "21": {
        "title": "Depreciation and Amortisation Expense",
        "full_title": "21. Depreciation and Amortisation Expense",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "Depreciation & amortisation",
                        "value": "{depreciation_amortisation_2024}",
                        "previous_value": "{depreciation_amortisation_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "21",
            "generated_on": "{generated_on}"
        }
    },
    "22": {
        "title": "Loss on Sale of Assets & Investments",
        "full_title": "22. Loss on Sale of Assets & Investments",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "Short Term Loss on Sale of Investments (Non Derivative Loss)",
                        "value": "{short_term_loss_investments_2024}",
                        "previous_value": "{short_term_loss_investments_2023}"
                    },
                    {
                        "label": "Long term loss on sale of investments",
                        "value": "{long_term_loss_investments_2024}",
                        "previous_value": "{long_term_loss_investments_2023}"
                    },
                    {
                        "label": "Loss on Sale of Fixed Assets",
                        "value": "{loss_fixed_assets_2024}",
                        "previous_value": "{loss_fixed_assets_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "22",
            "generated_on": "{generated_on}"
        }
    },
    "23": {
        "title": "Finance Costs",
        "full_title": "23. Finance Costs",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "Bank & Finance Charges",
                        "value": "{bank_finance_charges_2024}",
                        "previous_value": "{bank_finance_charges_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "23",
            "generated_on": "{generated_on}"
        }
    },
    "24": {
        "title": "Payment to Auditor",
        "full_title": "24. Payment to Auditor",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "For Audit fee",
                        "value": "{audit_fee_2024}",
                        "previous_value": "{audit_fee_2023}"
                    },
                    {
                        "label": "For Tax Audit / Certification Fees",
                        "value": "{tax_audit_certification_fees_2024}",
                        "previous_value": "{tax_audit_certification_fees_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "24",
            "generated_on": "{generated_on}"
        }
    },
    "25": {
        "title": "Earnings in Foreign Currency",
        "full_title": "25. Earnings in Foreign Currency",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Inflow",
                "subcategories": [
                    {
                        "label": "Income from export of services",
                        "value": "{income_export_services_2024}",
                        "previous_value": "{income_export_services_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "25",
            "generated_on": "{generated_on}"
        }
    },
    "26": {
        "title": "Particulars of Un-hedged Foreign Currency Exposure",
        "full_title": "26. Particulars of Un-hedged Foreign Currency Exposure",
        "structure": [
            {
                "category": "",
                "subcategories": [
                    {
                        "label": "March 31, 2024",
                        "value": "{march_2024_total}"
                    },
                    {
                        "label": "March 31, 2023",
                        "value": "{march_2023_total}"
                    }
                ]
            },
            {
                "category": "Inflow",
                "subcategories": [
                    {
                        "label": "Income from export of services",
                        "value": "{income_export_services_2024}",
                        "previous_value": "{income_export_services_2023}"
                    }
                ],
                "total": "{total_2024}",
                "previous_total": "{total_2023}"
            }
        ],
        "metadata": {
            "note_number": "26",
            "generated_on": "{generated_on}"
        },
        "notes_and_disclosures": [
            "(i) There is no derivate contract outstanding as at the Balance Sheet date.",
            "(ii) Particulars of un-hedged foreign currency exposure as at the Balance Sheet date"
        ]
    }
}

def generate_note_template(note_number, llm_data=None):
    """Generate a note template with placeholders for LLM to fill."""
    if note_number not in note_templates:
        return None
    
    template = note_templates[note_number].copy()
    template["metadata"]["generated_on"] = datetime.now().isoformat()
    
    # Placeholder values to be replaced by LLM
    if llm_data:
        for category in template["structure"]:
            if "total" in category:
                category["total"] = llm_data.get(f"{note_number}_total_2024", "{total_2024}")
                category["previous_total"] = llm_data.get(f"{note_number}_total_2023", "{total_2023}")
            for subcat in category.get("subcategories", []):
                for key in ["value", "previous_value"]:
                    if key in subcat:
                        field_name = subcat["label"].lower().replace(" ", "_").replace("-", "_").replace("/", "_").replace("&", "_")
                        subcat[key] = llm_data.get(f"{note_number}_{field_name}_{key.split('_')[0]}", f"{{{field_name}_{key.split('_')[0]}}}")
            for subcat in category.get("columns", []):
                subcat["value"] = llm_data.get(f"{note_number}_{subcat['header'].lower().replace(' ', '_').replace('-', '_')}_2024", f"{{{subcat['header'].lower().replace(' ', '_').replace('-', '_')}_2024}}")
            for subcat in category.get("values", []):
                subcat["value"] = llm_data.get(f"{note_number}_{subcat['period'].lower().replace(' ', '_').replace('-', '_')}_{subcat['label'].lower().replace(' ', '_')}_2024", f"{{{subcat['period'].lower().replace(' ', '_').replace('-', '_')}_{subcat['label'].lower().replace(' ', '_')}_2024}}")
    
    return template

def generate_all_notes():
    """Generate templates for all notes and save to JSON."""
    all_notes = {
        "metadata": {
            "generated_on": datetime.now().isoformat(),
            "financial_year": "2024-03-31",
            "company_name": "Your Company Name",
            "total_notes": len(note_templates)
        },
        "notes": []
    }
    
    for note_number in note_templates.keys():
        note = generate_note_template(note_number)
        if note:
            all_notes["notes"].append(note)
    
    with open("note_templates.json", "w", encoding="utf-8") as f:
        json.dump(all_notes, f, indent=2, ensure_ascii=False)
    
    return all_notes

if __name__ == "__main__":
    notes_data = generate_all_notes()
    print("Note templates generated and saved to note_templates.json")