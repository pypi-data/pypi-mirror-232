import aiohttp
from datetime import datetime, timedelta

api_url = "https://api.publisher.tonic.com"


class TonicAPIClient:
    def __init__(self, consumer_key, consumer_secret):
        self.api_url = "https://api.publisher.tonic.com"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.bearer = None
        self.token_expiration = None
        self.session = aiohttp.ClientSession()

    async def close_session(self):
        await self.session.close()

    async def get_bearer(self):
        if (
            self.bearer is not None
            and self.token_expiration is not None
            and datetime.now() < self.token_expiration
        ):
            return self.bearer

        request_url = f"{self.api_url}/jwt/authenticate"
        headers = {"Content-Type": "application/json"}
        body = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
        }

        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                bearer = await response.json()
                self.bearer = bearer["token"]
                self.token_expiration = datetime.now() + timedelta(minutes=90)
                return self.bearer
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    # CAMPAIGNS

    async def get_campaigns_list(self, state: str = "active", output: str = "json"):
        """
        Get campaign list

        Args:
            state (str, optional): The state of the campaigns you want to be listed (valid states are: incomplete, pending, active, stopped, deleted). Defaults to 'active'.
            output (str, optional): The output type you want to receive. Defaults to "json".

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/list"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "state": state,
            "output": output,
        }

        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def create_campaign(
        self,
        name: str,
        offer: str,
        country: str,
        offer_id: int = None,
        imprint: str = None,
    ):
        """
        Create Campaign

        Args:
            name (str): Campaign name
            offer (str): Offer Name
            country (str): Country code
            offer_id (int, optional): Offer ID (If offerId is provided, offer will be ignored and isn’t mandatory anymore). Defaults to None.
            imprint (str, optional): Default is yes for EU countries and no for non-EU countries.. Defaults to 'yes'.

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/create"
        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {
            "name": name,
            "offer": offer,
            "offer_id": offer_id,
            "country": country,
            "imprint": imprint,
        }

        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def set_keywords(
        self,
        campaign_id: int,
        keywords: list[str],
        country: str,
        keyword_amount: int = None,
    ):
        """
        Set keywords

        Args:
            campaign_id (int): Campaign ID
            keywords (list[str]): List of keywords. List will be converted to uniques list automatically by set()
            country (str): Country code
            keyword_amount (int): Keywords amount. Defaults to None. If None keywords amount will be calculated automatically

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/keywords"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        unique_keywords = list(set(keywords))
        body = {
            "campaign_id": campaign_id,
            "keywords": unique_keywords,
            "country": country,
            "keyword_amount": len(unique_keywords),
        }

        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def get_keywords(self, campaign_id: int):
        """
        Get campaign keywords

        Args:
            campaign_id (int): The campaign where you want to retrieve the keyword status from.

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/status"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "campaign_id": campaign_id,
        }

        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def get_campaign_status(self, name: str, id: int):
        """
        Get campaign status

        Args:
            name (str): Campaign name
            id (int): Campaign id (may be used instead of name)

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/status"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "name": name,
            "id": id,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def rename_campaign(self, campaign_id: int, campaign_name: str):
        """
        Get campaign status

        Args:
            campaign_id (int): The id of the campaign whose name shall be changed
            campaign_name (str): The new name for the campaign

        Returns:
            Status 200: "Campaign # was renamed to: test_name
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/rename"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "campaign_id": campaign_id,
            "campaign_name": campaign_name,
        }
        async with self.session.put(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def get_callback_urls(self, campaign_id: int):
        """
        Get Callback Urls

        Args:
            campaign_id (int): Campaign id

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/callback"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {"campaign_id": campaign_id}
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def set_callback(self, campaign_id: int, type: str, url: str):
        """
        Set Callback Urls

        Args:
            campaign_id (int): Campaign id
            type (str): Type of callback url (redirect, view, viewrt, click, estimated_revenue, estimated_revenue_5h, preestimated_revenue)
            url (str): Your callback url (make sure this is sent as an url-encoded value)

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/callback"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }

        body = {
            "campaign_id": campaign_id,
            "type": type,
            "url": url,
        }

        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def delete_callback(self, campaign_id: int, type: str):
        """
        Set Callback Urls

        Args:
            campaign_id (int): Campaign id
            type (str): Type of callback url (redirect, view, viewrt, click, estimated_revenue, estimated_revenue_5h, preestimated_revenue)

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/callback"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }

        body = {
            "campaign_id": campaign_id,
            "type": type,
        }

        async with self.session.delete(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    # PIXEL"""

    async def get_pixel(self, campaign_id: int):
        """
        Returns the data of an active pixel for the given campaign id.
        Currently the following types are supported:

        taboola
        outbrain
        yahoo
        facebook

        Args:
            campaign_id (int): Campaign ID

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "campaign_id": campaign_id,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def delete_pixel(self, campaign_id: int):
        """
        Deletes an active pixel for the given campaign id

        Args:
            campaign_id (int): Campaign ID

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {
            "campaign_id": campaign_id,
        }
        async with self.session.delete(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def invoke_pixel(self):
        """
        You can invoke a previously set up pixel in order to test the integration. Currently the following types are supported:
            Facebook
            Twitter
            TikTok
        Some networks provide test tokens for instant testing, you may forward them in the request body.

        Args:
            campaign_id (int): Campaign ID

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel/invoke"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {}
        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def create_tiktok_pixel(
        self, campaign_id: int, pixel: str, access_token: str
    ):
        """
        You can create a new TikTok pixel or overwrite an existing one. This will overwrite any other Pixel for this campaign.

        Important: You need to append ttclid=__CLICKID__ to the end of your URL in the TikTok Campaign in order to track conversions.

        How to use the TikTok Pixel:
        Sign in to your TikTok Ads Manager to gather the values that you will use to complete the tag setup:
            - In your TikTok Ads Manager Account, go to Assets -> Events
            - Click the Manage button for Web Events
            - If not already done create a Pixel:
                1. Select the Set Up Web Events button
                2. Type in a name
                3. Select Events API as Connection Method and click Next
                4. Select Manually Set Up Events API as Installation Type and click Next
                5. Select the Go to Settings button in the bottom right corner
            - If you have a Pixel:
                1. Click on the pixel name
                2. Go to the Settings tab
            - Copy the ID which is written underneath the pixel name and past it as Pixel Id
            - Click the Generate Access Token button under Events API
            - Copy the token and past it as Access Token

        Args:
            campaign_id (int): Campaign ID
            pixel_id (int): Pixel ID from TikTok Ads Manager Account
            access_token (str): Access Token from TikTok Ads Manager Account

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel/tiktok"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {
            "campaign_id": campaign_id,
            "pixel_id": pixel,
            "access_token": access_token,
        }
        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def set_pixel_tracking_facebook(
        self, campaign_id: int, pixel: str, access_token: str, event_type: str
    ):
        """
        Create Facebook Pixel

        Args:
            campaign_id (int): Campaign ID
            pixel_id (int): Pixel ID from TikTok Ads Manager Account
            access_token (str): Access Token from TikTok Ads Manager Account
            event_type (str): Event Type Name

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel/facebook"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {
            "campaign_id": campaign_id,
            "pixel_id": pixel,
            "access_token": access_token,
            "event_type": event_type,
        }
        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def set_pixel_tracking_taboola(
        self, campaign_id: int, pixel: str, access_token: str, event_type: str
    ):
        """
        Create Taboola Pixel
        You can create a new taboola pixel or overwrite an existing one. This will overwrite any other Pixel for this campaign. Important: You need to insert click_id={click_id} in the Field “tracking code” to activate S2S-Tracking.

        The allowed Values for the event name are:
            add_payment_info
            add_to_cart
            add_to_wishlist
            app_install
            complete_registration
            lead
            make_purchase
            search
            start_checkout
            view_content

        Important:
        You need to insert click_id={click_id} in the Field "tracking code" to activate S2S-Tracking. (See Taboola.com.)

        Args:
            campaign_id (int): Campaign ID
            event_name (str): Event type nane

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel/taboola"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {
            "campaign_id": campaign_id,
            "event_type": event_type,
        }
        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def set_pixel_tracking_outbrain(self, campaign_id: int, event_type: str):
        """
        Create Outbrain Pixel

        You can create a new outbrain pixel or overwrite an existing one. This will overwrite any other Pixel for this campaign.

        Important: You need to insert outbrainclickid={{ob_click_id}} in the campaign tracking box in Outbrain.

        Args:
            campaign_id (int): Campaign ID
            event_name (str): Event type name

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel/outbrain"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {
            "campaign_id": campaign_id,
            "event_type": event_type,
        }
        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def set_pixel_tracking_yahoo(
        self, campaign_id: int, pixel_id: str, event_type: str, yahoo_use_s2s: str
    ):
        """
        Create Outbrain Pixel

        You can create a new yahoo pixel or overwrite an existing one. This will overwrite any other Pixel for this campaign.

        Important: Make sure to attach vmcid=${CC} to your tracking link in yahoo

        You need to setup a conversion rule with a event definition having set Action -> Equals to to match the value of the Event Definition (Action) on this page.

        To do this, go to your Yahoo Native (formerly Gemini) backend, select SHARED LIBRARY > Conversion rules and create a new rule.

        The Dot-Tag-Id can be found in the conversion rules overview page or during the creation of a rule.

        See also https://developer.yahooinc.com/native/advertiser/guide/targeting/track-conversions/create-conversion-rule/

        Args:
            campaign_id (int): _description_
            pixel_id (str): _description_
            event_name (str): Event type. Defaults to "ClickButton"
            yahoo_use_s2s (str): Use Yahoo DSP S2S conversions. (recommended, see info box). Defaults to "yes"

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/campaign/pixel/outbrain"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        body = {
            "campaign_id": campaign_id,
            "pixel_id": pixel_id,
            "event_type": event_type,
            "yahoo_use_s2s": yahoo_use_s2s,
        }
        async with self.session.post(
            request_url, json=body, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    # IMPRINT

    async def set_imprint(self, name: str, imprint: str):
        """
        Set imprint

        Args:
            name (int): Campaign name
            imprint (str): Choices: yes no

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/imprint/set"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "name": name,
            "imprint": imprint,
        }
        async with self.session.put(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    # COUNTRIES

    async def get_countries_list_for_offer(
        self, offer: str, offer_id: int, output: str = "json"
    ):
        """
        Get a list of countries of an offer

        Args:
            offer (str): The Offer Name
            offer_id (int): Offer id ( If offerId is provided, offer will be ignored and isn’t mandatory anymore)
            output (str): Output format, default JSON

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/countries/combination"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "offer": offer,
            "offer_id": offer_id,
            "output": output,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def get_countries_list(self, output: str):
        """
        Get a list of all countries sorted by country code

        Args:
            output (str): Output format, default JSON

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/countries/list"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {"output": output}
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    # OFFERS

    async def get_offers_list(self, output: str):
        """
        Get a list of all offers

        Args:
            output (str): Output format, default JSON

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/offers/list"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {"output": output}
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def get_offers_list_for_country(self, country: str, output: str):
        """
        Get a list of offers for a country

        Args:
            country (str): The country code according to ISO 3166
            output (str): Output format, default JSON

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/offers/combination"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {"country": country, "output": output}
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    # EPC

    async def daily_epc_tracking(self, date: str, output: str):
        """
        Daily EPC Tracking

        Our EPC tracking allows you to gather valuable click data in almost real time. This means that you will see estimated revenues for single clicks after round about 2h depending on our system load.

        After we receive final Revenue data from our Partner we’ll apply corrections to the estimated revenue, so the data will match with our system-wide statistical data. This usually happens after 48 hours.

        Args:
            date (str): The date of the day you want to receive (YYYY-MM-DD)
            output (str): Output format, default JSON

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/epc/daily"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {"date": date, "output": output}
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def final_epc_tracking(
        self, from_date: str, to_date: str, hour: str, campaign_id: int, output: str
    ):
        """
        Final EPC Tracking

        Our EPC tracking allows you to gather valuable click data in almost real time. This means that you will see estimated revenues for single clicks after just 20 minutes to 1 hour depending on our system load. We track clicks on a daily basis grouped by domain, keyword and given tracking parameters (subid1, 2, 3 and 4).

        After our partners send the final data these will be visible in this API.

        You can request up to 31 days per call.

        EPC data only available from 2020-01-01

        Args:
            from_date (str): The date of the day you want to receive (YYYY-MM-DD)
            to_date (str): The date of the day you want to receive (YYYY-MM-DD)
            hour (str): The hour you want to receive, from 0 to 23, only possible when requesting a single day
            campaign_id (str): The campaign you want to receive the stats from
            output (str): Output format, default JSON

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/epc/final"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "from": from_date,
            "to": to_date,
            "hour": hour,
            "campaign_id": campaign_id,
            "output": output,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def five_hours_estimation_update(self):
        """
        5h estimation update

        The revenue estimation is updated after approximately five hours.
        This endpoint gives the exact date and time until which this estimation update is currently applied to the revenue of clicks.

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/epc/estimation_update_until"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {}
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    # OTHERS

    async def get_tracking_data_report(
        self,
        from_date: str = None,
        to_date: str = None,
        date: str = None,
        columns: str = None,
        output="json",
    ):
        """
        Tracking Data Report

        Args:
            from_date (str, optional): The end of the asked date range (maximum 31 days after ‘from’). Defaults to None.
            to_date (str, optional): The end of the asked date range (maximum 31 days after ‘from’). Defaults to None.
            date (str, optional): The date of the day you want to receive. If provided this will overwrite the date range. Therefore, ‘from’ and ‘to’ aren’t required if date is provided. Defaults to None.
            columns (str, optional): A comma-separated list of the columns you want to receive. Defaults to None.
            output (str, optional): The output type you want to receive. Defaults to "json".

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/reports/tracking"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "from": from_date,
            "to": to_date,
            "date": date,
            "columns": columns,
            "output": output,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def daily_session_tracking(
        self,
        date: str,
        hour: str = None,
        campaign_id: str = None,
        output="json",
    ):
        """
        Daily Session Tracking

        Args:
            date (str): The date of the day you want to receive (YYYY-MM-DD)
            hour (str, optional): The hour of the day you want to receive (0-23). Defaults to None.
            campaign_id (int, optional): The id of the campaign of of which you want to query the data. Defaults to None.
            output (str, optional): The output type you want to receive. Defaults to "json".

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/session/daily"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "date": date,
            "hour": hour,
            "campaign_id": campaign_id,
            "output": output,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def get_last_final_date(
        self,
        output="json",
    ):
        """
        Get last final date

        Args:
            output (str, optional): The output type you want to receive. Defaults to "json".

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/last/final"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "output": output,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }

    async def check_if_date_is_final(self, date: str):
        """
        Check if date is final

        Args:
            date (str): The date of the day you want to check (YYYY-MM-DD)

        Returns:
            Status 200: JSON Array
            Another statuses: {"status_code": status_code, "status_description": text}
        """
        request_url = f"{self.api_url}/privileged/v3/final/date"

        bearer = await self.get_bearer()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer}",
        }
        params = {
            "date": date,
        }
        async with self.session.get(
            request_url, params=params, headers=headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {
                    "status_code": response.status,
                    "status_description": await response.text(),
                }
