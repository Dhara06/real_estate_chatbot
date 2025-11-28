from django.shortcuts import render
import pandas as pd
import re
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from django.conf import settings


DATA_FILE = os.path.join(settings.BASE_DIR, 'Sample_data.xlsx')
COLUMN_MAP = {
    'year': 'year',
    'location': 'final_location',
    'city': 'city',
    'total_sales': 'total_sales_-_igr',
    'total_sold': 'total_sold_-_igr',
    'flat_sold': 'flat_sold_-_igr',
    'office_sold': 'office_sold_-_igr',
    'shop_sold': 'shop_sold_-_igr',
    'commercial_sold': 'commercial_sold_-_igr',
    'residential_sold': 'residential_sold_-_igr',
    'flat_rate': 'flat_-_weighted_average_rate',
    'office_rate': 'office_-_weighted_average_rate',
    'shop_rate': 'shop_-_weighted_average_rate',
    'total_units': 'total_units',
    'carpet_area': 'total_carpet_area_supplied_(sqft)',
    'flat_total': 'flat_total',
    'shop_total': 'shop_total',
    'office_total': 'office_total'
}

def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()
    
def extract_locations(query):
    query_lower = query.lower()
    df = load_data()
    if df.empty:
        return []
    
    found_locations = []
    if 'final_location' in df.columns:
        unique_locations = df['final_location'].unique()
        for location in unique_locations:
            if pd.notna(location) and location.lower() in query_lower:
                found_locations.append(location)
    
    return found_locations

def format_currency(value):
    if pd.isna(value) or value == 0:
        return "N/A"
    if value >= 10000000:
        return f"₹{value/10000000:.2f} Cr"
    elif value >= 100000:
        return f"₹{value/100000:.2f} L"
    else:
        return f"₹{value:,.0f}"

def get_query_type(query):
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus', 'between']):
        return 'compare'
    elif any(word in query_lower for word in ['trend', 'growth', 'over time', 'yearly', 'year']):
        return 'trend'
    elif any(word in query_lower for word in ['rate', 'price', 'cost', 'average rate']):
        return 'rate'
    elif any(word in query_lower for word in ['sales', 'sold', 'transaction']):
        return 'sales'
    else:
        return 'overview'
    
def generate_summary(df, locations, query):
    if df.empty or not locations:
        return "No data available for the specified location(s)."
    
    query_type = get_query_type(query)
    filtered_df = df[df['final_location'].isin(locations)]
    
    if filtered_df.empty:
        return f"No data found for {', '.join(locations)}."
    
    try:
        if query_type == 'compare' and len(locations) >= 2:
            loc1, loc2 = locations[0], locations[1]
            df1 = df[df['final_location'] == loc1]
            df2 = df[df['final_location'] == loc2]
            
            total_sales1 = df1['total_sales_-_igr'].sum()
            total_sales2 = df2['total_sales_-_igr'].sum()
            avg_flat_rate1 = df1['flat_-_weighted_average_rate'].mean()
            avg_flat_rate2 = df2['flat_-_weighted_average_rate'].mean()
            
            return f"Comparison: {loc1} has total IGR sales of {format_currency(total_sales1)} with avg flat rate {format_currency(avg_flat_rate1)}/sqft, while {loc2} has {format_currency(total_sales2)} with avg rate {format_currency(avg_flat_rate2)}/sqft. {loc1 if total_sales1 > total_sales2 else loc2} shows higher sales volume."
        
        elif query_type == 'trend':
            total_sales = filtered_df.groupby('year')['total_sales_-_igr'].sum()
            if len(total_sales) > 1:
                growth = ((total_sales.iloc[-1] - total_sales.iloc[0]) / total_sales.iloc[0] * 100) if total_sales.iloc[0] > 0 else 0
                return f"Sales trend for {', '.join(locations)}: Total IGR sales grew by {growth:.1f}% from {total_sales.index[0]} to {total_sales.index[-1]}. Peak sales occurred in {total_sales.idxmax()} with {format_currency(total_sales.max())}."
            else:
                return f"Limited trend data available for {', '.join(locations)}."
        
        elif query_type == 'rate':
            avg_flat_rate = filtered_df['flat_-_weighted_average_rate'].mean()
            avg_office_rate = filtered_df['office_-_weighted_average_rate'].mean()
            avg_shop_rate = filtered_df['shop_-_weighted_average_rate'].mean()
            
            rates = []
            if pd.notna(avg_flat_rate) and avg_flat_rate > 0:
                rates.append(f"Flat: {format_currency(avg_flat_rate)}/sqft")
            if pd.notna(avg_office_rate) and avg_office_rate > 0:
                rates.append(f"Office: {format_currency(avg_office_rate)}/sqft")
            if pd.notna(avg_shop_rate) and avg_shop_rate > 0:
                rates.append(f"Shop: {format_currency(avg_shop_rate)}/sqft")
            
            return f"Average property rates in {', '.join(locations)}: {', '.join(rates)}. Based on {len(filtered_df)} transactions."
        
        elif query_type == 'sales':
            total_sales = filtered_df['total_sales_-_igr'].sum()
            total_units = filtered_df['total_units'].sum()
            flat_sold = filtered_df['flat_sold_-_igr'].sum()
            
            return f"Sales data for {', '.join(locations)}: Total IGR sales amount to {format_currency(total_sales)} across {int(total_units)} units. Flats sold: {int(flat_sold)}. This represents significant market activity."
        
        else:
            total_sales = filtered_df['total_sales_-_igr'].sum()
            avg_flat_rate = filtered_df['flat_-_weighted_average_rate'].mean()
            total_carpet_area = filtered_df['total_carpet_area_supplied_(sqft)'].sum()
            total_units = filtered_df['total_units'].sum()
            
            return f"Market overview for {', '.join(locations)}: Total IGR sales of {format_currency(total_sales)} across {int(total_units)} units. Average flat rate: {format_currency(avg_flat_rate)}/sqft. Total carpet area: {total_carpet_area:,.0f} sqft."
    
    except Exception as e:
        print(f"Error generating summary: {e}")
        return f"Analysis complete for {', '.join(locations)}. {len(filtered_df)} records found."

def prepare_detailed_stats(filtered_df, locations, query_type):
    """Prepare comprehensive statistics from the filtered dataframe"""
    
    stats = {
        "locations": locations,
        "query_type": query_type,
        "total_records": len(filtered_df),
        "years_covered": sorted(filtered_df['year'].unique().tolist()) if 'year' in filtered_df.columns else []
    }
    
    
    stats["overall"] = {
        "total_sales_igr": float(filtered_df['total_sales_-_igr'].sum()) if 'total_sales_-_igr' in filtered_df.columns else 0,
        "total_units": int(filtered_df['total_units'].sum()) if 'total_units' in filtered_df.columns else 0,
        "total_carpet_area": float(filtered_df['total_carpet_area_supplied_(sqft)'].sum()) if 'total_carpet_area_supplied_(sqft)' in filtered_df.columns else 0,
    }
    
    
    stats["property_breakdown"] = {
        "flats_sold": int(filtered_df['flat_sold_-_igr'].sum()) if 'flat_sold_-_igr' in filtered_df.columns else 0,
        "offices_sold": int(filtered_df['office_sold_-_igr'].sum()) if 'office_sold_-_igr' in filtered_df.columns else 0,
        "shops_sold": int(filtered_df['shop_sold_-_igr'].sum()) if 'shop_sold_-_igr' in filtered_df.columns else 0,
        "commercial_sold": int(filtered_df['commercial_sold_-_igr'].sum()) if 'commercial_sold_-_igr' in filtered_df.columns else 0,
        "residential_sold": int(filtered_df['residential_sold_-_igr'].sum()) if 'residential_sold_-_igr' in filtered_df.columns else 0,
    }
    
    
    stats["average_rates"] = {
        "flat_rate_per_sqft": float(filtered_df['flat_-_weighted_average_rate'].mean()) if 'flat_-_weighted_average_rate' in filtered_df.columns else 0,
        "office_rate_per_sqft": float(filtered_df['office_-_weighted_average_rate'].mean()) if 'office_-_weighted_average_rate' in filtered_df.columns else 0,
        "shop_rate_per_sqft": float(filtered_df['shop_-_weighted_average_rate'].mean()) if 'shop_-_weighted_average_rate' in filtered_df.columns else 0,
    }
    
    
    if len(stats["years_covered"]) > 1:
        yearly_data = filtered_df.groupby('year').agg({
            'total_sales_-_igr': 'sum',
            'total_units': 'sum',
            'flat_-_weighted_average_rate': 'mean'
        }).reset_index()
        
        stats["yearly_trends"] = []
        for _, row in yearly_data.iterrows():
            stats["yearly_trends"].append({
                "year": int(row['year']),
                "total_sales": float(row['total_sales_-_igr']),
                "total_units": int(row['total_units']),
                "avg_flat_rate": float(row['flat_-_weighted_average_rate']) if pd.notna(row['flat_-_weighted_average_rate']) else 0
            })
        
       
        if len(yearly_data) > 1:
            first_year_sales = yearly_data.iloc[0]['total_sales_-_igr']
            last_year_sales = yearly_data.iloc[-1]['total_sales_-_igr']
            if first_year_sales > 0:
                stats["growth_rate"] = float(((last_year_sales - first_year_sales) / first_year_sales) * 100)
            else:
                stats["growth_rate"] = 0
    
    
    if len(locations) > 1:
        stats["location_comparison"] = []
        for loc in locations:
            loc_data = filtered_df[filtered_df['final_location'] == loc]
            stats["location_comparison"].append({
                "location": loc,
                "total_sales": float(loc_data['total_sales_-_igr'].sum()),
                "total_units": int(loc_data['total_units'].sum()),
                "avg_flat_rate": float(loc_data['flat_-_weighted_average_rate'].mean()) if pd.notna(loc_data['flat_-_weighted_average_rate'].mean()) else 0
            })
    
    return stats

def generate_llm_summary(filtered_df, locations, query):
    """Generate LLM-based summary using actual Excel data"""
    if filtered_df.empty:
        return "No data available for the selected locations."

    query_type = get_query_type(query)
    
   
    detailed_stats = prepare_detailed_stats(filtered_df, locations, query_type)

    #Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0.3  #Lower temperature for more factual responses
    )

    
    trend_section = ""
    if "yearly_trends" in detailed_stats and len(detailed_stats["yearly_trends"]) > 1:
        trend_section = "YEAR-WISE TRENDS:\n"
        for trend in detailed_stats["yearly_trends"]:
            trend_section += f"- {trend['year']}: Sales ₹{trend['total_sales']:,.0f}, Units {trend['total_units']}, Avg Rate ₹{trend['avg_flat_rate']:,.0f}/sqft\n"
        if "growth_rate" in detailed_stats:
            trend_section += f"Overall Growth Rate: {detailed_stats['growth_rate']:.1f}%\n"
    
    
    comparison_section = ""
    if "location_comparison" in detailed_stats:
        comparison_section = "LOCATION COMPARISON:\n"
        for comp in detailed_stats["location_comparison"]:
            comparison_section += f"- {comp['location']}: Sales ₹{comp['total_sales']:,.0f}, Units {comp['total_units']}, Avg Rate ₹{comp['avg_flat_rate']:,.0f}/sqft\n"

    
    prompt = PromptTemplate.from_template("""
You are a professional real estate market analyst. Analyze the following ACTUAL data from the Excel dataset and provide insights.

User Query: {query}

ACTUAL DATA FROM EXCEL:
=======================
Locations Analyzed: {locations}
Total Records: {total_records}
Years Covered: {years_covered}

OVERALL METRICS:
- Total IGR Sales: ₹{total_sales:,.0f}
- Total Units Sold: {total_units}
- Total Carpet Area: {total_carpet_area:,.0f} sqft

PROPERTY TYPE BREAKDOWN:
- Flats Sold: {flats_sold}
- Offices Sold: {offices_sold}
- Shops Sold: {shops_sold}
- Commercial Properties: {commercial_sold}
- Residential Properties: {residential_sold}

AVERAGE RATES (per sqft):
- Flat Rate: ₹{flat_rate:,.0f}
- Office Rate: ₹{office_rate:,.0f}
- Shop Rate: ₹{shop_rate:,.0f}

{trend_section}

{comparison_section}

Based on this ACTUAL data, provide a concise, professional analysis covering:
1. Market strength and performance
2. Key trends or patterns
3. Investment outlook

Keep the response under 150 words. Use specific numbers from the data above.
""")

   
    chain = prompt | llm

    response = chain.invoke({
        "query": query,
        "locations": ", ".join(locations),
        "total_records": detailed_stats["total_records"],
        "years_covered": ", ".join(map(str, detailed_stats["years_covered"])),
        "total_sales": detailed_stats["overall"]["total_sales_igr"],
        "total_units": detailed_stats["overall"]["total_units"],
        "total_carpet_area": detailed_stats["overall"]["total_carpet_area"],
        "flats_sold": detailed_stats["property_breakdown"]["flats_sold"],
        "offices_sold": detailed_stats["property_breakdown"]["offices_sold"],
        "shops_sold": detailed_stats["property_breakdown"]["shops_sold"],
        "commercial_sold": detailed_stats["property_breakdown"]["commercial_sold"],
        "residential_sold": detailed_stats["property_breakdown"]["residential_sold"],
        "flat_rate": detailed_stats["average_rates"]["flat_rate_per_sqft"],
        "office_rate": detailed_stats["average_rates"]["office_rate_per_sqft"],
        "shop_rate": detailed_stats["average_rates"]["shop_rate_per_sqft"],
        "trend_section": trend_section,
        "comparison_section": comparison_section
    })

    return response.content.strip()


@api_view(['POST'])
def analyze_query(request):
    query = request.data.get('query', '')
    
    if not query:
        return Response({
            'error': 'Query is required',
            'summary': '',
            'chartData': [],
            'tableData': [],
            'metrics': {}
        }, status=400)
    
    df = load_data()
    if df.empty:
        return Response({
            'summary': 'Data file not found. Please ensure Sample_data.xlsx exists in backend folder.',
            'chartData': [],
            'tableData': [],
            'metrics': {}
        })

    locations = extract_locations(query)
    
    if not locations:
        return Response({
            'summary': 'No recognized location found. Please specify a location from your dataset.',
            'chartData': [],
            'tableData': [],
            'metrics': {}
        })
        
    filtered_df = df[df['final_location'].isin(locations)]
    
    if filtered_df.empty:
        return Response({
            'summary': f'No data found for {", ".join(locations)}.',
            'chartData': [],
            'tableData': [],
            'metrics': {}
        })
        
    try:
        summary = generate_llm_summary(filtered_df, locations, query)
    except Exception as e:
        print("Groq LLM failed:", e)
        summary = generate_summary(df, locations, query)

    
    query_type = get_query_type(query)
    chart_data = []
    chart_type = 'line'
    
    if query_type == 'compare' and len(locations) >= 2:
        chart_type = 'bar'
        for loc in locations[:5]:  # Max 5 locations for comparison
            loc_data = df[df['final_location'] == loc]
            total_sales = loc_data['total_sales_-_igr'].sum()
            chart_data.append({
                'label': loc,
                'value': float(total_sales) if pd.notna(total_sales) else 0
            })
    else:
        # Time series data
        grouped = filtered_df.groupby('year').agg({
            'total_sales_-_igr': 'sum',
            'flat_-_weighted_average_rate': 'mean'
        }).reset_index()
        
        chart_data = [
            {
                'year': int(row['year']),
                'totalSales': float(row['total_sales_-_igr']) if pd.notna(row['total_sales_-_igr']) else 0,
                'flatRate': float(row['flat_-_weighted_average_rate']) if pd.notna(row['flat_-_weighted_average_rate']) else 0
            }
            for _, row in grouped.iterrows()
        ]
        
    metrics = {}
    try:
        total_sales = filtered_df['total_sales_-_igr'].sum()
        total_units = filtered_df['total_units'].sum()
        avg_flat_rate = filtered_df['flat_-_weighted_average_rate'].mean()
        total_carpet = filtered_df['total_carpet_area_supplied_(sqft)'].sum()
        
        metrics = {
            'Total Sales': format_currency(total_sales),
            'Total Units': f"{int(total_units):,}" if pd.notna(total_units) else "N/A",
            'Avg Flat Rate': format_currency(avg_flat_rate),
            'Carpet Area': f"{int(total_carpet):,} sqft" if pd.notna(total_carpet) else "N/A"
        }
    except Exception as e:
        print(f"Error calculating metrics: {e}")
        
    table_data = []
    if not filtered_df.empty:
        
        display_cols = ['year', 'final_location', 'total_sales_-_igr', 'flat_sold_-_igr', 
                       'flat_-_weighted_average_rate', 'total_units', 'total_carpet_area_supplied_(sqft)']
        
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        table_df = filtered_df[available_cols].copy()
        
        
        table_df.columns = ['year', 'final_location', 'total_sales_igr', 'flat_sold_igr', 
                           'flat_weighted_avg_rate', 'total_units', 'total_carpet_area'][:len(available_cols)]
        
        table_data = table_df.to_dict('records')
        
    return Response({
        'summary': summary,
        'chartData': chart_data,
        'chartType': chart_type,
        'tableData': table_data,
        'metrics': metrics
    })   
    
@api_view(['GET'])
def health_check(request):
    df = load_data()
    locations = []
    if not df.empty and 'final_location' in df.columns:
        locations = df['final_location'].unique().tolist()[:10]
    
    return Response({
        'status': 'ok',
        'message': 'API is running',
        'data_loaded': not df.empty,
        'total_records': len(df),
        'sample_locations': locations
    })