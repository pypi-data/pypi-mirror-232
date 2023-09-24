# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: anki/scheduler.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from anki import generic_pb2 as anki_dot_generic__pb2
from anki import cards_pb2 as anki_dot_cards__pb2
from anki import decks_pb2 as anki_dot_decks__pb2
from anki import collection_pb2 as anki_dot_collection__pb2
from anki import config_pb2 as anki_dot_config__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x61nki/scheduler.proto\x12\x0e\x61nki.scheduler\x1a\x12\x61nki/generic.proto\x1a\x10\x61nki/cards.proto\x1a\x10\x61nki/decks.proto\x1a\x15\x61nki/collection.proto\x1a\x11\x61nki/config.proto\"\xbf\t\n\x0fSchedulingState\x12\x38\n\x06normal\x18\x01 \x01(\x0b\x32&.anki.scheduler.SchedulingState.NormalH\x00\x12<\n\x08\x66iltered\x18\x02 \x01(\x0b\x32(.anki.scheduler.SchedulingState.FilteredH\x00\x12\x18\n\x0b\x63ustom_data\x18\x03 \x01(\tH\x01\x88\x01\x01\x1a\x17\n\x03New\x12\x10\n\x08position\x18\x01 \x01(\r\x1a\x84\x01\n\x08Learning\x12\x17\n\x0fremaining_steps\x18\x01 \x01(\r\x12\x16\n\x0escheduled_secs\x18\x02 \x01(\r\x12\x36\n\x0cmemory_state\x18\x06 \x01(\x0b\x32\x1b.anki.cards.FsrsMemoryStateH\x00\x88\x01\x01\x42\x0f\n\r_memory_state\x1a\xb5\x01\n\x06Review\x12\x16\n\x0escheduled_days\x18\x01 \x01(\r\x12\x14\n\x0c\x65lapsed_days\x18\x02 \x01(\r\x12\x13\n\x0b\x65\x61se_factor\x18\x03 \x01(\x02\x12\x0e\n\x06lapses\x18\x04 \x01(\r\x12\x0f\n\x07leeched\x18\x05 \x01(\x08\x12\x36\n\x0cmemory_state\x18\x06 \x01(\x0b\x32\x1b.anki.cards.FsrsMemoryStateH\x00\x88\x01\x01\x42\x0f\n\r_memory_state\x1a\x80\x01\n\nRelearning\x12\x36\n\x06review\x18\x01 \x01(\x0b\x32&.anki.scheduler.SchedulingState.Review\x12:\n\x08learning\x18\x02 \x01(\x0b\x32(.anki.scheduler.SchedulingState.Learning\x1a\xfe\x01\n\x06Normal\x12\x32\n\x03new\x18\x01 \x01(\x0b\x32#.anki.scheduler.SchedulingState.NewH\x00\x12<\n\x08learning\x18\x02 \x01(\x0b\x32(.anki.scheduler.SchedulingState.LearningH\x00\x12\x38\n\x06review\x18\x03 \x01(\x0b\x32&.anki.scheduler.SchedulingState.ReviewH\x00\x12@\n\nrelearning\x18\x04 \x01(\x0b\x32*.anki.scheduler.SchedulingState.RelearningH\x00\x42\x06\n\x04kind\x1a\x33\n\x07Preview\x12\x16\n\x0escheduled_secs\x18\x01 \x01(\r\x12\x10\n\x08\x66inished\x18\x02 \x01(\x08\x1aT\n\x12ReschedulingFilter\x12>\n\x0eoriginal_state\x18\x01 \x01(\x0b\x32&.anki.scheduler.SchedulingState.Normal\x1a\x9a\x01\n\x08\x46iltered\x12:\n\x07preview\x18\x01 \x01(\x0b\x32\'.anki.scheduler.SchedulingState.PreviewH\x00\x12J\n\x0crescheduling\x18\x02 \x01(\x0b\x32\x32.anki.scheduler.SchedulingState.ReschedulingFilterH\x00\x42\x06\n\x04kindB\x06\n\x04kindB\x0e\n\x0c_custom_data\"\xf8\x02\n\x0bQueuedCards\x12\x35\n\x05\x63\x61rds\x18\x01 \x03(\x0b\x32&.anki.scheduler.QueuedCards.QueuedCard\x12\x11\n\tnew_count\x18\x02 \x01(\r\x12\x16\n\x0elearning_count\x18\x03 \x01(\r\x12\x14\n\x0creview_count\x18\x04 \x01(\r\x1a\xc4\x01\n\nQueuedCard\x12\x1e\n\x04\x63\x61rd\x18\x01 \x01(\x0b\x32\x10.anki.cards.Card\x12\x30\n\x05queue\x18\x02 \x01(\x0e\x32!.anki.scheduler.QueuedCards.Queue\x12\x30\n\x06states\x18\x03 \x01(\x0b\x32 .anki.scheduler.SchedulingStates\x12\x32\n\x07\x63ontext\x18\x04 \x01(\x0b\x32!.anki.scheduler.SchedulingContext\"*\n\x05Queue\x12\x07\n\x03NEW\x10\x00\x12\x0c\n\x08LEARNING\x10\x01\x12\n\n\x06REVIEW\x10\x02\"L\n\x15GetQueuedCardsRequest\x12\x13\n\x0b\x66\x65tch_limit\x18\x01 \x01(\r\x12\x1e\n\x16intraday_learning_only\x18\x02 \x01(\x08\"E\n\x18SchedTimingTodayResponse\x12\x14\n\x0c\x64\x61ys_elapsed\x18\x01 \x01(\r\x12\x13\n\x0bnext_day_at\x18\x02 \x01(\x03\"<\n\x1aStudiedTodayMessageRequest\x12\r\n\x05\x63\x61rds\x18\x01 \x01(\r\x12\x0f\n\x07seconds\x18\x02 \x01(\x01\"i\n\x12UpdateStatsRequest\x12\x0f\n\x07\x64\x65\x63k_id\x18\x01 \x01(\x03\x12\x11\n\tnew_delta\x18\x02 \x01(\x05\x12\x14\n\x0creview_delta\x18\x04 \x01(\x05\x12\x19\n\x11millisecond_delta\x18\x05 \x01(\x05\"O\n\x13\x45xtendLimitsRequest\x12\x0f\n\x07\x64\x65\x63k_id\x18\x01 \x01(\x03\x12\x11\n\tnew_delta\x18\x02 \x01(\x05\x12\x14\n\x0creview_delta\x18\x03 \x01(\x05\"9\n\x1a\x43ountsForDeckTodayResponse\x12\x0b\n\x03new\x18\x01 \x01(\x05\x12\x0e\n\x06review\x18\x02 \x01(\x05\"\x8b\x02\n\x14\x43ongratsInfoResponse\x12\x17\n\x0flearn_remaining\x18\x01 \x01(\r\x12\x1d\n\x15secs_until_next_learn\x18\x02 \x01(\r\x12\x18\n\x10review_remaining\x18\x03 \x01(\x08\x12\x15\n\rnew_remaining\x18\x04 \x01(\x08\x12\x19\n\x11have_sched_buried\x18\x05 \x01(\x08\x12\x18\n\x10have_user_buried\x18\x06 \x01(\x08\x12\x18\n\x10is_filtered_deck\x18\x07 \x01(\x08\x12!\n\x19\x62ridge_commands_supported\x18\x08 \x01(\x08\x12\x18\n\x10\x64\x65\x63k_description\x18\t \x01(\t\"\x8a\x01\n\x11UnburyDeckRequest\x12\x0f\n\x07\x64\x65\x63k_id\x18\x01 \x01(\x03\x12\x34\n\x04mode\x18\x02 \x01(\x0e\x32&.anki.scheduler.UnburyDeckRequest.Mode\".\n\x04Mode\x12\x07\n\x03\x41LL\x10\x00\x12\x0e\n\nSCHED_ONLY\x10\x01\x12\r\n\tUSER_ONLY\x10\x02\"\xb1\x01\n\x19\x42uryOrSuspendCardsRequest\x12\x10\n\x08\x63\x61rd_ids\x18\x01 \x03(\x03\x12\x10\n\x08note_ids\x18\x02 \x03(\x03\x12<\n\x04mode\x18\x03 \x01(\x0e\x32..anki.scheduler.BuryOrSuspendCardsRequest.Mode\"2\n\x04Mode\x12\x0b\n\x07SUSPEND\x10\x00\x12\x0e\n\nBURY_SCHED\x10\x01\x12\r\n\tBURY_USER\x10\x02\"\xe5\x01\n\x19ScheduleCardsAsNewRequest\x12\x10\n\x08\x63\x61rd_ids\x18\x01 \x03(\x03\x12\x0b\n\x03log\x18\x02 \x01(\x08\x12\x18\n\x10restore_position\x18\x03 \x01(\x08\x12\x14\n\x0creset_counts\x18\x04 \x01(\x08\x12G\n\x07\x63ontext\x18\x05 \x01(\x0e\x32\x31.anki.scheduler.ScheduleCardsAsNewRequest.ContextH\x00\x88\x01\x01\"$\n\x07\x43ontext\x12\x0b\n\x07\x42ROWSER\x10\x00\x12\x0c\n\x08REVIEWER\x10\x01\x42\n\n\x08_context\"g\n!ScheduleCardsAsNewDefaultsRequest\x12\x42\n\x07\x63ontext\x18\x01 \x01(\x0e\x32\x31.anki.scheduler.ScheduleCardsAsNewRequest.Context\"T\n\"ScheduleCardsAsNewDefaultsResponse\x12\x18\n\x10restore_position\x18\x01 \x01(\x08\x12\x14\n\x0creset_counts\x18\x02 \x01(\x08\"m\n\x11SetDueDateRequest\x12\x10\n\x08\x63\x61rd_ids\x18\x01 \x03(\x03\x12\x0c\n\x04\x64\x61ys\x18\x02 \x01(\t\x12\x38\n\nconfig_key\x18\x03 \x01(\x0b\x32$.anki.config.OptionalStringConfigKey\"y\n\x10SortCardsRequest\x12\x10\n\x08\x63\x61rd_ids\x18\x01 \x03(\x03\x12\x15\n\rstarting_from\x18\x02 \x01(\r\x12\x11\n\tstep_size\x18\x03 \x01(\r\x12\x11\n\trandomize\x18\x04 \x01(\x08\x12\x16\n\x0eshift_existing\x18\x05 \x01(\x08\"5\n\x0fSortDeckRequest\x12\x0f\n\x07\x64\x65\x63k_id\x18\x01 \x01(\x03\x12\x11\n\trandomize\x18\x02 \x01(\x08\"\x81\x02\n\x10SchedulingStates\x12\x30\n\x07\x63urrent\x18\x01 \x01(\x0b\x32\x1f.anki.scheduler.SchedulingState\x12.\n\x05\x61gain\x18\x02 \x01(\x0b\x32\x1f.anki.scheduler.SchedulingState\x12-\n\x04hard\x18\x03 \x01(\x0b\x32\x1f.anki.scheduler.SchedulingState\x12-\n\x04good\x18\x04 \x01(\x0b\x32\x1f.anki.scheduler.SchedulingState\x12-\n\x04\x65\x61sy\x18\x05 \x01(\x0b\x32\x1f.anki.scheduler.SchedulingState\"\xa7\x02\n\nCardAnswer\x12\x0f\n\x07\x63\x61rd_id\x18\x01 \x01(\x03\x12\x36\n\rcurrent_state\x18\x02 \x01(\x0b\x32\x1f.anki.scheduler.SchedulingState\x12\x32\n\tnew_state\x18\x03 \x01(\x0b\x32\x1f.anki.scheduler.SchedulingState\x12\x31\n\x06rating\x18\x04 \x01(\x0e\x32!.anki.scheduler.CardAnswer.Rating\x12\x1a\n\x12\x61nswered_at_millis\x18\x05 \x01(\x03\x12\x1a\n\x12milliseconds_taken\x18\x06 \x01(\r\"1\n\x06Rating\x12\t\n\x05\x41GAIN\x10\x00\x12\x08\n\x04HARD\x10\x01\x12\x08\n\x04GOOD\x10\x02\x12\x08\n\x04\x45\x41SY\x10\x03\"\xd6\x03\n\x12\x43ustomStudyRequest\x12\x0f\n\x07\x64\x65\x63k_id\x18\x01 \x01(\x03\x12\x19\n\x0fnew_limit_delta\x18\x02 \x01(\x05H\x00\x12\x1c\n\x12review_limit_delta\x18\x03 \x01(\x05H\x00\x12\x15\n\x0b\x66orgot_days\x18\x04 \x01(\rH\x00\x12\x1b\n\x11review_ahead_days\x18\x05 \x01(\rH\x00\x12\x16\n\x0cpreview_days\x18\x06 \x01(\rH\x00\x12\x37\n\x04\x63ram\x18\x07 \x01(\x0b\x32\'.anki.scheduler.CustomStudyRequest.CramH\x00\x1a\xe7\x01\n\x04\x43ram\x12>\n\x04kind\x18\x01 \x01(\x0e\x32\x30.anki.scheduler.CustomStudyRequest.Cram.CramKind\x12\x12\n\ncard_limit\x18\x02 \x01(\r\x12\x17\n\x0ftags_to_include\x18\x03 \x03(\t\x12\x17\n\x0ftags_to_exclude\x18\x04 \x03(\t\"Y\n\x08\x43ramKind\x12\x11\n\rCRAM_KIND_DUE\x10\x00\x12\x11\n\rCRAM_KIND_NEW\x10\x01\x12\x14\n\x10\x43RAM_KIND_REVIEW\x10\x02\x12\x11\n\rCRAM_KIND_ALL\x10\x03\x42\x07\n\x05value\"4\n\x11SchedulingContext\x12\x11\n\tdeck_name\x18\x01 \x01(\t\x12\x0c\n\x04seed\x18\x02 \x01(\x04\"-\n\x1a\x43ustomStudyDefaultsRequest\x12\x0f\n\x07\x64\x65\x63k_id\x18\x01 \x01(\x03\"\xb8\x02\n\x1b\x43ustomStudyDefaultsResponse\x12=\n\x04tags\x18\x01 \x03(\x0b\x32/.anki.scheduler.CustomStudyDefaultsResponse.Tag\x12\x12\n\nextend_new\x18\x02 \x01(\r\x12\x15\n\rextend_review\x18\x03 \x01(\r\x12\x15\n\ravailable_new\x18\x04 \x01(\r\x12\x18\n\x10\x61vailable_review\x18\x05 \x01(\r\x12!\n\x19\x61vailable_new_in_children\x18\x06 \x01(\r\x12$\n\x1c\x61vailable_review_in_children\x18\x07 \x01(\r\x1a\x35\n\x03Tag\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07include\x18\x02 \x01(\x08\x12\x0f\n\x07\x65xclude\x18\x03 \x01(\x08\";\n\x1aRepositionDefaultsResponse\x12\x0e\n\x06random\x18\x01 \x01(\x08\x12\r\n\x05shift\x18\x02 \x01(\x08\"+\n\x19\x43omputeFsrsWeightsRequest\x12\x0e\n\x06search\x18\x01 \x01(\t\"A\n\x1a\x43omputeFsrsWeightsResponse\x12\x0f\n\x07weights\x18\x01 \x03(\x02\x12\x12\n\nfsrs_items\x18\x02 \x01(\r\"\xaa\x01\n\x1e\x43omputeOptimalRetentionRequest\x12\x0f\n\x07weights\x18\x01 \x03(\x02\x12\x11\n\tdeck_size\x18\x02 \x01(\r\x12\x18\n\x10\x64\x61ys_to_simulate\x18\x03 \x01(\r\x12$\n\x1cmax_seconds_of_study_per_day\x18\x04 \x01(\r\x12\x14\n\x0cmax_interval\x18\x05 \x01(\r\x12\x0e\n\x06search\x18\x06 \x01(\t\"<\n\x1f\x43omputeOptimalRetentionResponse\x12\x19\n\x11optimal_retention\x18\x01 \x01(\x02\"\xa8\x03\n\x1aOptimalRetentionParameters\x12\x18\n\x10recall_secs_hard\x18\x06 \x01(\x01\x12\x18\n\x10recall_secs_good\x18\x07 \x01(\x01\x12\x18\n\x10recall_secs_easy\x18\x08 \x01(\x01\x12\x13\n\x0b\x66orget_secs\x18\t \x01(\x01\x12\x12\n\nlearn_secs\x18\n \x01(\x01\x12&\n\x1e\x66irst_rating_probability_again\x18\x0b \x01(\x01\x12%\n\x1d\x66irst_rating_probability_hard\x18\x0c \x01(\x01\x12%\n\x1d\x66irst_rating_probability_good\x18\r \x01(\x01\x12%\n\x1d\x66irst_rating_probability_easy\x18\x0e \x01(\x01\x12&\n\x1ereview_rating_probability_hard\x18\x0f \x01(\x01\x12&\n\x1ereview_rating_probability_good\x18\x10 \x01(\x01\x12&\n\x1ereview_rating_probability_easy\x18\x11 \x01(\x01\"6\n$GetOptimalRetentionParametersRequest\x12\x0e\n\x06search\x18\x01 \x01(\t\"c\n%GetOptimalRetentionParametersResponse\x12:\n\x06params\x18\x01 \x01(\x0b\x32*.anki.scheduler.OptimalRetentionParameters\"9\n\x16\x45valuateWeightsRequest\x12\x0f\n\x07weights\x18\x01 \x03(\x02\x12\x0e\n\x06search\x18\x02 \x01(\t\">\n\x17\x45valuateWeightsResponse\x12\x10\n\x08log_loss\x18\x01 \x01(\x02\x12\x11\n\trmse_bins\x18\x02 \x01(\x02\x32\xcd\x14\n\x10SchedulerService\x12T\n\x0eGetQueuedCards\x12%.anki.scheduler.GetQueuedCardsRequest\x1a\x1b.anki.scheduler.QueuedCards\x12\x44\n\nAnswerCard\x12\x1a.anki.scheduler.CardAnswer\x1a\x1a.anki.collection.OpChanges\x12Q\n\x10SchedTimingToday\x12\x13.anki.generic.Empty\x1a(.anki.scheduler.SchedTimingTodayResponse\x12\x39\n\x0cStudiedToday\x12\x13.anki.generic.Empty\x1a\x14.anki.generic.String\x12W\n\x13StudiedTodayMessage\x12*.anki.scheduler.StudiedTodayMessageRequest\x1a\x14.anki.generic.String\x12\x46\n\x0bUpdateStats\x12\".anki.scheduler.UpdateStatsRequest\x1a\x13.anki.generic.Empty\x12H\n\x0c\x45xtendLimits\x12#.anki.scheduler.ExtendLimitsRequest\x1a\x13.anki.generic.Empty\x12T\n\x12\x43ountsForDeckToday\x12\x12.anki.decks.DeckId\x1a*.anki.scheduler.CountsForDeckTodayResponse\x12I\n\x0c\x43ongratsInfo\x12\x13.anki.generic.Empty\x1a$.anki.scheduler.CongratsInfoResponse\x12Q\n\x1eRestoreBuriedAndSuspendedCards\x12\x13.anki.cards.CardIds\x1a\x1a.anki.collection.OpChanges\x12K\n\nUnburyDeck\x12!.anki.scheduler.UnburyDeckRequest\x1a\x1a.anki.collection.OpChanges\x12\x64\n\x12\x42uryOrSuspendCards\x12).anki.scheduler.BuryOrSuspendCardsRequest\x1a#.anki.collection.OpChangesWithCount\x12\x43\n\x11\x45mptyFilteredDeck\x12\x12.anki.decks.DeckId\x1a\x1a.anki.collection.OpChanges\x12N\n\x13RebuildFilteredDeck\x12\x12.anki.decks.DeckId\x1a#.anki.collection.OpChangesWithCount\x12[\n\x12ScheduleCardsAsNew\x12).anki.scheduler.ScheduleCardsAsNewRequest\x1a\x1a.anki.collection.OpChanges\x12\x83\x01\n\x1aScheduleCardsAsNewDefaults\x12\x31.anki.scheduler.ScheduleCardsAsNewDefaultsRequest\x1a\x32.anki.scheduler.ScheduleCardsAsNewDefaultsResponse\x12K\n\nSetDueDate\x12!.anki.scheduler.SetDueDateRequest\x1a\x1a.anki.collection.OpChanges\x12R\n\tSortCards\x12 .anki.scheduler.SortCardsRequest\x1a#.anki.collection.OpChangesWithCount\x12P\n\x08SortDeck\x12\x1f.anki.scheduler.SortDeckRequest\x1a#.anki.collection.OpChangesWithCount\x12K\n\x13GetSchedulingStates\x12\x12.anki.cards.CardId\x1a .anki.scheduler.SchedulingStates\x12P\n\x12\x44\x65scribeNextStates\x12 .anki.scheduler.SchedulingStates\x1a\x18.anki.generic.StringList\x12\x43\n\x0cStateIsLeech\x12\x1f.anki.scheduler.SchedulingState\x1a\x12.anki.generic.Bool\x12<\n\x10UpgradeScheduler\x12\x13.anki.generic.Empty\x1a\x13.anki.generic.Empty\x12M\n\x0b\x43ustomStudy\x12\".anki.scheduler.CustomStudyRequest\x1a\x1a.anki.collection.OpChanges\x12n\n\x13\x43ustomStudyDefaults\x12*.anki.scheduler.CustomStudyDefaultsRequest\x1a+.anki.scheduler.CustomStudyDefaultsResponse\x12U\n\x12RepositionDefaults\x12\x13.anki.generic.Empty\x1a*.anki.scheduler.RepositionDefaultsResponse\x12k\n\x12\x43omputeFsrsWeights\x12).anki.scheduler.ComputeFsrsWeightsRequest\x1a*.anki.scheduler.ComputeFsrsWeightsResponse\x12\x8c\x01\n\x1dGetOptimalRetentionParameters\x12\x34.anki.scheduler.GetOptimalRetentionParametersRequest\x1a\x35.anki.scheduler.GetOptimalRetentionParametersResponse\x12z\n\x17\x43omputeOptimalRetention\x12..anki.scheduler.ComputeOptimalRetentionRequest\x1a/.anki.scheduler.ComputeOptimalRetentionResponse\x12\x62\n\x0f\x45valuateWeights\x12&.anki.scheduler.EvaluateWeightsRequest\x1a\'.anki.scheduler.EvaluateWeightsResponse2\x19\n\x17\x42\x61\x63kendSchedulerServiceB\x02P\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'anki.scheduler_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'P\001'
  _SCHEDULINGSTATE._serialized_start=139
  _SCHEDULINGSTATE._serialized_end=1354
  _SCHEDULINGSTATE_NEW._serialized_start=304
  _SCHEDULINGSTATE_NEW._serialized_end=327
  _SCHEDULINGSTATE_LEARNING._serialized_start=330
  _SCHEDULINGSTATE_LEARNING._serialized_end=462
  _SCHEDULINGSTATE_REVIEW._serialized_start=465
  _SCHEDULINGSTATE_REVIEW._serialized_end=646
  _SCHEDULINGSTATE_RELEARNING._serialized_start=649
  _SCHEDULINGSTATE_RELEARNING._serialized_end=777
  _SCHEDULINGSTATE_NORMAL._serialized_start=780
  _SCHEDULINGSTATE_NORMAL._serialized_end=1034
  _SCHEDULINGSTATE_PREVIEW._serialized_start=1036
  _SCHEDULINGSTATE_PREVIEW._serialized_end=1087
  _SCHEDULINGSTATE_RESCHEDULINGFILTER._serialized_start=1089
  _SCHEDULINGSTATE_RESCHEDULINGFILTER._serialized_end=1173
  _SCHEDULINGSTATE_FILTERED._serialized_start=1176
  _SCHEDULINGSTATE_FILTERED._serialized_end=1330
  _QUEUEDCARDS._serialized_start=1357
  _QUEUEDCARDS._serialized_end=1733
  _QUEUEDCARDS_QUEUEDCARD._serialized_start=1493
  _QUEUEDCARDS_QUEUEDCARD._serialized_end=1689
  _QUEUEDCARDS_QUEUE._serialized_start=1691
  _QUEUEDCARDS_QUEUE._serialized_end=1733
  _GETQUEUEDCARDSREQUEST._serialized_start=1735
  _GETQUEUEDCARDSREQUEST._serialized_end=1811
  _SCHEDTIMINGTODAYRESPONSE._serialized_start=1813
  _SCHEDTIMINGTODAYRESPONSE._serialized_end=1882
  _STUDIEDTODAYMESSAGEREQUEST._serialized_start=1884
  _STUDIEDTODAYMESSAGEREQUEST._serialized_end=1944
  _UPDATESTATSREQUEST._serialized_start=1946
  _UPDATESTATSREQUEST._serialized_end=2051
  _EXTENDLIMITSREQUEST._serialized_start=2053
  _EXTENDLIMITSREQUEST._serialized_end=2132
  _COUNTSFORDECKTODAYRESPONSE._serialized_start=2134
  _COUNTSFORDECKTODAYRESPONSE._serialized_end=2191
  _CONGRATSINFORESPONSE._serialized_start=2194
  _CONGRATSINFORESPONSE._serialized_end=2461
  _UNBURYDECKREQUEST._serialized_start=2464
  _UNBURYDECKREQUEST._serialized_end=2602
  _UNBURYDECKREQUEST_MODE._serialized_start=2556
  _UNBURYDECKREQUEST_MODE._serialized_end=2602
  _BURYORSUSPENDCARDSREQUEST._serialized_start=2605
  _BURYORSUSPENDCARDSREQUEST._serialized_end=2782
  _BURYORSUSPENDCARDSREQUEST_MODE._serialized_start=2732
  _BURYORSUSPENDCARDSREQUEST_MODE._serialized_end=2782
  _SCHEDULECARDSASNEWREQUEST._serialized_start=2785
  _SCHEDULECARDSASNEWREQUEST._serialized_end=3014
  _SCHEDULECARDSASNEWREQUEST_CONTEXT._serialized_start=2966
  _SCHEDULECARDSASNEWREQUEST_CONTEXT._serialized_end=3002
  _SCHEDULECARDSASNEWDEFAULTSREQUEST._serialized_start=3016
  _SCHEDULECARDSASNEWDEFAULTSREQUEST._serialized_end=3119
  _SCHEDULECARDSASNEWDEFAULTSRESPONSE._serialized_start=3121
  _SCHEDULECARDSASNEWDEFAULTSRESPONSE._serialized_end=3205
  _SETDUEDATEREQUEST._serialized_start=3207
  _SETDUEDATEREQUEST._serialized_end=3316
  _SORTCARDSREQUEST._serialized_start=3318
  _SORTCARDSREQUEST._serialized_end=3439
  _SORTDECKREQUEST._serialized_start=3441
  _SORTDECKREQUEST._serialized_end=3494
  _SCHEDULINGSTATES._serialized_start=3497
  _SCHEDULINGSTATES._serialized_end=3754
  _CARDANSWER._serialized_start=3757
  _CARDANSWER._serialized_end=4052
  _CARDANSWER_RATING._serialized_start=4003
  _CARDANSWER_RATING._serialized_end=4052
  _CUSTOMSTUDYREQUEST._serialized_start=4055
  _CUSTOMSTUDYREQUEST._serialized_end=4525
  _CUSTOMSTUDYREQUEST_CRAM._serialized_start=4285
  _CUSTOMSTUDYREQUEST_CRAM._serialized_end=4516
  _CUSTOMSTUDYREQUEST_CRAM_CRAMKIND._serialized_start=4427
  _CUSTOMSTUDYREQUEST_CRAM_CRAMKIND._serialized_end=4516
  _SCHEDULINGCONTEXT._serialized_start=4527
  _SCHEDULINGCONTEXT._serialized_end=4579
  _CUSTOMSTUDYDEFAULTSREQUEST._serialized_start=4581
  _CUSTOMSTUDYDEFAULTSREQUEST._serialized_end=4626
  _CUSTOMSTUDYDEFAULTSRESPONSE._serialized_start=4629
  _CUSTOMSTUDYDEFAULTSRESPONSE._serialized_end=4941
  _CUSTOMSTUDYDEFAULTSRESPONSE_TAG._serialized_start=4888
  _CUSTOMSTUDYDEFAULTSRESPONSE_TAG._serialized_end=4941
  _REPOSITIONDEFAULTSRESPONSE._serialized_start=4943
  _REPOSITIONDEFAULTSRESPONSE._serialized_end=5002
  _COMPUTEFSRSWEIGHTSREQUEST._serialized_start=5004
  _COMPUTEFSRSWEIGHTSREQUEST._serialized_end=5047
  _COMPUTEFSRSWEIGHTSRESPONSE._serialized_start=5049
  _COMPUTEFSRSWEIGHTSRESPONSE._serialized_end=5114
  _COMPUTEOPTIMALRETENTIONREQUEST._serialized_start=5117
  _COMPUTEOPTIMALRETENTIONREQUEST._serialized_end=5287
  _COMPUTEOPTIMALRETENTIONRESPONSE._serialized_start=5289
  _COMPUTEOPTIMALRETENTIONRESPONSE._serialized_end=5349
  _OPTIMALRETENTIONPARAMETERS._serialized_start=5352
  _OPTIMALRETENTIONPARAMETERS._serialized_end=5776
  _GETOPTIMALRETENTIONPARAMETERSREQUEST._serialized_start=5778
  _GETOPTIMALRETENTIONPARAMETERSREQUEST._serialized_end=5832
  _GETOPTIMALRETENTIONPARAMETERSRESPONSE._serialized_start=5834
  _GETOPTIMALRETENTIONPARAMETERSRESPONSE._serialized_end=5933
  _EVALUATEWEIGHTSREQUEST._serialized_start=5935
  _EVALUATEWEIGHTSREQUEST._serialized_end=5992
  _EVALUATEWEIGHTSRESPONSE._serialized_start=5994
  _EVALUATEWEIGHTSRESPONSE._serialized_end=6056
  _SCHEDULERSERVICE._serialized_start=6059
  _SCHEDULERSERVICE._serialized_end=8696
  _BACKENDSCHEDULERSERVICE._serialized_start=8698
  _BACKENDSCHEDULERSERVICE._serialized_end=8723
# @@protoc_insertion_point(module_scope)
