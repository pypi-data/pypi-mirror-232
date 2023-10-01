def is_code_redemption_only(game):
    return game['isCodeRedemptionOnly']


def games_info(data, status):
    game_info = []

    for game in data:
        if is_code_redemption_only(game) is False:
            prices = game['price']['totalPrice']['fmtPrice']

            game_data = {
                'title': game['title'],
                'description': game['description'],
                'offerType': game['offerType'],
                'originalPrice': prices['originalPrice'],
                'discountPrice': prices['discountPrice'],
                'seller': game['seller']['name'],
                'gameSlug': game['productSlug'] or game['urlSlug'],
                'gameImgUrl': game['keyImages'][0]['url']
            }

            if status == 'ALL':
                game_info.append(game_data)

    return game_info
