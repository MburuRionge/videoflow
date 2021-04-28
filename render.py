# Render a batch of videos with the 'Render' tag

import os
from flo.idea import Idea
from flo.trello import Trello
from flo.davinci import Davinci
from flo.channel import Channel
from flo.videoflo import VideoFlo
from flo.mactag import update_tag


# loop over videos ready to be rendered
def loop(channel, davinci, trello):
    renderable = trello.get_list('Render', channel)
    total = len(renderable)
    print('Rendering {} videos for {}'.format(total, channel.name))

    counter = 0
    finished = 0
    for item in renderable:
        card_id = item['id']
        name = item['name']
        path = trello.find_path_for_id(card_id, channel)
        if path is None:
            print('Could not find local path for {}'.format(name))
            continue

        counter = counter + 1
        project_name = os.path.basename(path)
        idea = Idea()
        idea.from_project(project_name, channel)
        if not idea.exists():
            print('Directory for {} not found'.format(project_name))
            return

        davinci.load_project(idea)
        print('Rendering {}/{} ({})'.format(counter, total, idea.name))
        success = davinci.render_video()
        if success:
            update_tag('Upload', idea.path)
            success = trello.move_card(idea, 'Upload')
        finished = finished + 1 if success else finished

    if total == 0:
        print('Nothing to render')
    else:
        print('Rendered {}/{} videos'.format(finished, total))

def go():
    davinci = Davinci()
    if davinci.resolve is None:
        return
    davinci.open_deliver_page()

    flo = VideoFlo()
    args = flo.get_channel_arguments()
    channel = Channel(flo.config, args.channel)

    trello = Trello()
    if not trello.lists_exist(['Render', 'Upload'], channel):
        return

    loop(channel, davinci, trello)

go()
