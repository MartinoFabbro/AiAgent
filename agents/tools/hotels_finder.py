import os
from typing import Optional
import serpapi
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool

class HotelsInput(BaseModel):
    q: str = Field(description='Location of the hotel')
    check_in_date: str = Field(description='Check-in date. The format is YYYY-MM-DD. e.g. 2024-06-22')
    check_out_date: str = Field(description='Check-out date. The format is YYYY-MM-DD. e.g. 2024-06-28')
    sort_by: Optional[str] = Field(default='8', description='Parameter is used for sorting the results. Default is sort by highest rating')
    adults: Optional[int] = Field(default=1, description='Number of adults. Default to 1.')
    children: Optional[int] = Field(default=0, description='Number of children. Default to 0.')
    rooms: Optional[int] = Field(default=1, description='Number of rooms. Default to 1.')
    hotel_class: Optional[str] = Field(default=None, description='Parameter defines to include only certain hotel class in the results. for example- 2,3,4')

class HotelsInputSchema(BaseModel):
    params: HotelsInput

@tool(args_schema=HotelsInputSchema)
def hotels_finder(params: HotelsInput):
    '''
    Find hotels using the Google Hotels engine.
    
    Returns:
        list: Top 5 hotel search results with processed information.
    '''
    try:
        # Prepare search parameters
        search_params = {
            'api_key': os.environ.get('SERPAPI_API_KEY'),
            'engine': 'google_hotels',
            'hl': 'en',
            'gl': 'us',
            'q': params.q,
            'check_in_date': params.check_in_date,
            'check_out_date': params.check_out_date,
            'currency': 'USD',
            'adults': params.adults,
            'children': params.children,
            'rooms': params.rooms,
            'sort_by': params.sort_by
        }

        # Add hotel class if specified
        if params.hotel_class:
            search_params['hotel_class'] = params.hotel_class

        # Perform search
        search = serpapi.search(search_params)
        
        # Process and extract results
        raw_properties = search.data.get('properties', [])
        
        # Process and clean up hotel information
        processed_hotels = []
        for hotel in raw_properties[:5]:
            processed_hotel = {
                'name': hotel.get('name', 'Unknown Hotel'),
                'price': hotel.get('price', 'Price not available'),
                'rating': hotel.get('rating', 'No rating'),
                'reviews_count': hotel.get('reviews_count', 'No reviews'),
                'description': hotel.get('description', 'No description'),
                'amenities': hotel.get('amenities', []),
                'link': hotel.get('link', ''),
                'image': hotel.get('thumbnail', '')
            }
            processed_hotels.append(processed_hotel)
        
        return processed_hotels

    except Exception as e:
        # Improved error handling
        return {
            'error': f"Error in hotel search: {str(e)}",
            'params': str(search_params)
        }