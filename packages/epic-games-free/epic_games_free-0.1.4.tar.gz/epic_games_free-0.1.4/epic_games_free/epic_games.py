import epic_games_free.utils as utils
import typing
import requests

Any = typing.Any
Optional = typing.Optional

__all__ = (
    'EpicGames'
)


class EpicGames:
    def __init__(self,
                 locale: Optional[str] = "en-US",
                 country: Optional[str] = "US",
                 allow_countries: Optional[str] = "US"
                 ) -> None:
        """
        Epic Games Free Class

        Args:
            locale (str, optional): Locale. Defaults to "en-US".
            country (str, optional): Country. Defaults to "US".
            allow_countries (str, optional): AllowCountries. Defaults to "US".
        """
        self.__locale = locale
        self.__country = country
        self.__allow_countries = allow_countries

    @property
    def locale(self) -> str:
        """
        Return locale

        Returns:
            str: Locale
        """
        return self.__locale

    @locale.setter
    def locale(self, locale) -> None:
        self.__locale = locale

    @property
    def country(self):
        """
        Return country

        Returns:
            str: Country
        """
        return self.__locale

    @country.setter
    def country(self, country) -> None:
        self.__country = country

    @property
    def allow_countries(self):
        """
        Returns allow_countries

        Returns:
            str: AllowCountries
        """
        return self.__allow_countries

    @allow_countries.setter
    def allow_countries(self, allow_countries) -> None:
        self.__allow_countries = allow_countries

    def fetch_data(self):
        """
        Returns dict of free games from EGS API

        Returns:
            dict: Dict of free games from EGS API
        """
        data = self._get_elements(self._get_response())
        return data

    def get_info_all_games(self) -> list[dict[str, Any]]:
        """
        All games info

        Returns:
            list[dict[str, Any]]: A list of dictionaries containing information about all free games.
                Each dictionary has the following keys:
                    - 'title': Game title.
                    - 'description': Game description.
                    - 'offerType': Type of gift (Base Game, DLC etc).
                    - 'originalPrice': Original price of a game.
                    - 'discountPrice': Discount price of a game.
                    - 'seller': Name of a seller.
                    - 'gameSlug': Game slug.
                    - 'gameImgUrl': Game image url.


        """
        data = self.fetch_data()
        games = utils.games_info(data, 'ALL')
        return games

    def get_title(
            self,
            index_of_element: Optional[int] = 0,
    ) -> str:
        """
        Returns one game title by index. Defaults to 0.

        Args:
            index_of_element (int, optional)
                Index of element in dict

        Returns:
            str: Locale
        """
        data = self.fetch_data()

        try:
            return data[index_of_element]['title']
        except IndexError:
            return data[len(data) - 1]['title']

    def get_titles(
            self,
    ) -> tuple:
        """
        Returns all game titles
        """
        data = self.fetch_data()

        return tuple([game['title'] for game in data])

    def _get_response(
            self
    ) -> dict:
        """
        Requests response from EGS free games backend

        Returns:
            Requested dict from EGS API
        """
        with requests.get('https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions?'
                          f'locale={self.__locale}&country={self.__country}&allowCountries={self.__allow_countries}') \
                as response:
            return response.json()

    @staticmethod
    def _get_elements(
            response: dict
    ) -> dict:
        """
        Returns response elements

        Parameters:
            response (dict): Response dictionary

        Returns:
            Elements dictionary
        """
        return response['data']['Catalog']['searchStore']['elements']

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        ...
