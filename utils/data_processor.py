
import pandas as pd
import numpy as np

class VahanDataProcessor:
    """
    Data processor for vehicle registration data from Vahan portal
    """

    def __init__(self):
        self.data = None

    def calculate_yoy_growth(self, df):
        """Calculate Year-over-Year growth"""
        # Sort by relevant columns
        df_sorted = df.sort_values(['state', 'category', 'manufacturer', 'year', 'quarter'])

        # Calculate YoY growth
        df_sorted['yoy_growth'] = df_sorted.groupby(['state', 'category', 'manufacturer', 'quarter'])['registrations'].pct_change(periods=1) * 100

        return df_sorted

    def calculate_qoq_growth(self, df):
        """Calculate Quarter-over-Quarter growth"""
        # Create quarter order mapping
        quarter_order = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
        df['quarter_num'] = df['quarter'].map(quarter_order)

        # Sort by year and quarter
        df_sorted = df.sort_values(['state', 'category', 'manufacturer', 'year', 'quarter_num'])

        # Calculate QoQ growth
        df_sorted['qoq_growth'] = df_sorted.groupby(['state', 'category', 'manufacturer'])['registrations'].pct_change(periods=1) * 100

        return df_sorted

    def get_summary_stats(self, df):
        """Get summary statistics for the dashboard"""
        total_vehicles = df['registrations'].sum()
        avg_growth = df['yoy_growth'].mean()
        top_category = df.groupby('category')['registrations'].sum().idxmax()
        top_manufacturer = df.groupby('manufacturer')['registrations'].sum().idxmax()

        return {
            'total_vehicles': f"{total_vehicles:,}",
            'avg_growth': f"{avg_growth:.1f}%",
            'top_category': top_category,
            'top_manufacturer': top_manufacturer
        }

    def filter_data(self, df, filters):
        """Apply filters to dataframe"""
        filtered_df = df.copy()

        if filters.get('years'):
            filtered_df = filtered_df[filtered_df['year'].isin(filters['years'])]

        if filters.get('states'):
            filtered_df = filtered_df[filtered_df['state'].isin(filters['states'])]

        if filters.get('categories'):
            filtered_df = filtered_df[filtered_df['category'].isin(filters['categories'])]

        if filters.get('manufacturers'):
            filtered_df = filtered_df[filtered_df['manufacturer'].isin(filters['manufacturers'])]

        return filtered_df
