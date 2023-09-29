""""LiveChatScraper class, used to scrape live chat data from a youtube stream."""
import time
from math import floor

# import constants.node_constants
from livechat_scraper.constants import node_constants as nc
from livechat_scraper.constants import scraper_constants as con
from livechat_scraper.builders.player_state import PlayerState
from livechat_scraper.generators.output_generator import OutputGenerator
from livechat_scraper.messages.chat_message import ChatMessage
from livechat_scraper.messages.membership_gifted_message import MembershipGiftedMessage
from livechat_scraper.messages.membership_message import MembershipChatMessage
from livechat_scraper.messages.pinned_message import PinnedMessage
from livechat_scraper.messages.superchat_message import SuperChatMessage
from livechat_scraper.requestors.subsequent_requestor import SubsequentRequestor
from livechat_scraper.scrapers.scraper_initializer import ScraperInitializer
from livechat_scraper.scrapers.video import Video

CONTINUATION_FETCH_BASE_URL = "https://www.youtube.com/youtubei/v1/next?"

class LiveChatScraper:
    """"entry point for live chat scraper, this is exposed object 
    that someone would use to scrape livechat contents"""
    output_filename = 'outputContent.json'
    invalid_characters = "<>:\"/\\|?*"
    sleepValue = 3

    def __init__(self, video_url, debug_mode = False):
        self.video = Video(None,video_url, None)
        self.is_debugging = debug_mode
        self.content_set = []
        self.__extract_video_id()
        self.player_state = PlayerState()
        self.end_time = 0
        self.initialization_successful = False
        self.requestor = None
        
    def __set_initial_parameters(self):
        try:

            self.player_state.continuation = ScraperInitializer()\
                .generate_initial_state(self.video.video_id)
            initial_content = ScraperInitializer().generate_initial_content(self.video.video_url)
            self.video.video_title = self.__clean_filename(initial_content["videoDetails"]["title"])
            self.output_filename = f'{self.video.video_title}_{time.time()}'
            self.end_time = int(initial_content["streamingData"]["formats"][0]["approxDurationMs"])
            self.initialization_successful = True
        except Exception:
            print("error encountered attempting to set initial parameters.")

    def __extract_video_id(self):
        key_start = self.video.video_url.find('watch')+8
        if key_start <= 8:
            key_start = self.video.video_url.find("live/")+5
        key_end = key_start + self.video.VIDEO_ID_LENGTH
        self.video.video_id = self.video.video_url[key_start:key_end]

    def __clean_filename(self, output_filename):
        for char in self.invalid_characters:
            output_filename = output_filename.replace(char, '')
        return output_filename

    def __parse_subsequent_contents(self):
        self.requestor.make_request()
        try:
            action_contents = self.requestor.response["continuationContents"]\
                ["liveChatContinuation"]["actions"][1::]
            for content in action_contents:
                self.content_set.append(content["replayChatItemAction"])
            self.player_state.continuation = self.requestor.update_continuation\
                (self.requestor.response)
            self.player_state.player_offset_ms = self.__find_final_offset_time()
            self.requestor.update_fetcher\
                (self.player_state.continuation, self.player_state.player_offset_ms)
        except KeyError:
            print(self.requestor.response)
            self.player_state.continuation = con.SCRAPE_FINISHED

    def __find_final_offset_time(self):
        final_content = self.content_set[-1]
        return final_content["videoOffsetTimeMsec"]

    def scrape(self):
        """method to call scrape functionality and pull livechat data."""
        self.__set_initial_parameters()
        if not self.initialization_successful:
            print("Unable to initialize scraper successfully, quitting")
            return False
        self.requestor = SubsequentRequestor(self.video.video_id, self.player_state)
        self.requestor.build_fetcher()
        print('Beginning livechat scraping')
        self.__parse_subsequent_contents()
        has_slept = True
        current_interval = 0
        while(int(self.player_state.player_offset_ms) < self.end_time \
            and self.player_state.continuation != con.SCRAPE_FINISHED):
            try:
                progress = float(self.player_state.player_offset_ms)/float(self.end_time)
                print(f'progress: {progress:.2%}', end="\r")
                floored_progress = floor(progress * 100)
                if current_interval != floored_progress:
                    has_slept = False
                if(floored_progress % 10 == 0 and not has_slept):
                    time.sleep(self.sleepValue)
                    current_interval = floored_progress
                    has_slept = True
                self.__parse_subsequent_contents()
            except Exception as ex:
                print("scraping failed")
                print(f"Exception encountered: {str(ex)}")
        print("scraping completed")
        return True

    def output_messages(self):
        """"build a messages list that contains all the chat messages"""
        messages = []
        for content in self.content_set:
            payload = content[nc.ACTIONS_NODE][0]
            if nc.TICKER_ITEM_ACTION_NODE in payload:
                pass
            elif nc.ADD_BANNER_NODE in payload:
                pinned_message = PinnedMessage(payload)
                pinned_message.build_message()
                messages.append(pinned_message.generate_content())
            elif nc.LIVECHAT_PAID_MESSAGE_NODE \
                in payload[nc.ADD_CHAT_ITEM_ACTION_NODE][nc.ITEM_NODE]:
                superchat = SuperChatMessage(payload)
                superchat.build_message()
                messages.append(superchat.generate_content())
            elif nc.LIVECHAT_MEMBERSHIP_NODE \
                in payload[nc.ADD_CHAT_ITEM_ACTION_NODE][nc.ITEM_NODE]:
                membership = MembershipChatMessage(payload)
                membership.build_message()
                messages.append(membership.generate_content())
            elif nc.LIVECHAT_MEMBERSHIP_GIFT_PURCHASED_ANNOUNCEMENT_NODE \
                in payload[nc.ADD_CHAT_ITEM_ACTION_NODE][nc.ITEM_NODE]:
                membership_gift = MembershipGiftedMessage(payload)
                membership_gift.build_message()
                messages.append(membership_gift.generate_content())
            elif nc.LIVECHAT_TEXT_MESSAGE_RENDERER_NODE \
                in payload[nc.ADD_CHAT_ITEM_ACTION_NODE][nc.ITEM_NODE]:
                chat = ChatMessage(payload)
                chat.build_message()
                messages.append(chat.generate_content())
        return messages

    def write_to_file(self, write_type, output_filename = None):
        """"writes currently scraped content to a file output"""
        if output_filename is None:
            output_filename = f'{write_type}_{self.output_filename}'
        generator = OutputGenerator(output_filename)
        if write_type != con.OUTPUT_RAW:
            generator.generate(self.output_messages(), write_type)
        else:
            generator.generate(self.content_set, write_type)
