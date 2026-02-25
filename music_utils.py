from yandex_music import Client, Cover

client = Client().init()


def simple_search(query):

    search_result = client.search(query)
    if search_result.best:
        type_ = search_result.best.type
        best = search_result.best.result
        if type_ == 'track':
            return best
    return None


def download_cover(query, user_id):
    track = simple_search(query)
    if not track:
        file_name = None
        return file_name

    print(track)

    title = track.title
    artist = ''
    for artists in track.artists:
        artist = artist + artists.name + ', '
    artist = artist[:-2]
    link = f'music.yandex.ru/album/{track.albums[0].id}/track/{track.id}'
    print(title, artist, link)

    file_name = f'img/cover_{user_id}.png'

    cover = Cover(
        uri=track.cover_uri,
        client=client
    )

    cover.download(
        filename=file_name,
        size="600x600"
    )

    return file_name, title, artist, link
