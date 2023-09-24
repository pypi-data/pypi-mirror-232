import os
from enum import Enum
from typing import Union


class Fields(object):
    """ Names for different application fields
    """
    cv = 'cv'
    nlp = 'nlp'
    audio = 'audio'
    multi_modal = 'multi-modal'
    science = 'science'


# ############################################ Hook ############################################

class Priority(Enum):
    """Hook priority levels.

    +--------------+------------+
    | Level        | Value      |
    +==============+============+
    | HIGHEST      | 0          |
    +--------------+------------+
    | VERY_HIGH    | 10         |
    +--------------+------------+
    | HIGH         | 30         |
    +--------------+------------+
    | ABOVE_NORMAL | 40         |
    +--------------+------------+
    | NORMAL       | 50         |
    +--------------+------------+
    | BELOW_NORMAL | 60         |
    +--------------+------------+
    | LOW          | 70         |
    +--------------+------------+
    | VERY_LOW     | 90         |
    +--------------+------------+
    | LOWEST       | 100        |
    +--------------+------------+
    """

    HIGHEST = 0
    VERY_HIGH = 10
    HIGH = 30
    ABOVE_NORMAL = 40
    NORMAL = 50
    BELOW_NORMAL = 60
    LOW = 70
    VERY_LOW = 90
    LOWEST = 100


def get_priority(priority: Union[int, str, Priority]) -> int:
    """Get priority value.

    Args:
        priority (int or str or :obj:`Priority`): Priority.

    Returns:
        int: The priority value.
    """
    if isinstance(priority, int):
        if priority < 0 or priority > 100:
            raise ValueError('priority must be between 0 and 100')
        return priority
    elif isinstance(priority, Priority):
        return priority.value
    elif isinstance(priority, str):
        return Priority[priority.upper()].value
    else:
        raise TypeError('priority must be an integer or Priority enum value')


class TrainerStages:
    before_init = 'before_init'
    after_init = 'after_init'
    before_run = 'before_run'
    before_val = 'before_val'
    before_train_epoch = 'before_train_epoch'
    before_train_iter = 'before_train_iter'
    after_train_iter = 'after_train_iter'
    after_train_epoch = 'after_train_epoch'
    before_val_epoch = 'before_val_epoch'
    before_val_iter = 'before_val_iter'
    after_val_iter = 'after_val_iter'
    after_val_epoch = 'after_val_epoch'
    after_run = 'after_run'
    after_val = 'after_val'


class Hooks(object):
    """ Names for different hooks.

        All kinds of hooks are defined here
    """
    # lr
    LrSchedulerHook = 'LrSchedulerHook'
    PlateauLrSchedulerHook = 'PlateauLrSchedulerHook'
    NoneLrSchedulerHook = 'NoneLrSchedulerHook'

    # optimizer
    OptimizerHook = 'OptimizerHook'
    TorchAMPOptimizerHook = 'TorchAMPOptimizerHook'
    ApexAMPOptimizerHook = 'ApexAMPOptimizerHook'
    NoneOptimizerHook = 'NoneOptimizerHook'

    # checkpoint
    CheckpointHook = 'CheckpointHook'
    BestCkptSaverHook = 'BestCkptSaverHook'
    LoadCheckpointHook = 'LoadCheckpointHook'

    # logger
    TextLoggerHook = 'TextLoggerHook'
    TensorboardHook = 'TensorboardHook'

    IterTimerHook = 'IterTimerHook'
    EvaluationHook = 'EvaluationHook'

    # Compression
    SparsityHook = 'SparsityHook'

    # CLIP logit_scale clamp
    ClipClampLogitScaleHook = 'ClipClampLogitScaleHook'

    # train
    EarlyStopHook = 'EarlyStopHook'
    DeepspeedHook = 'DeepspeedHook'
    MegatronHook = 'MegatronHook'
    DDPHook = 'DDPHook'


# ############################################ Metric ############################################

class MetricKeys(object):
    ACCURACY = 'accuracy'
    F1 = 'f1'
    Binary_F1 = 'binary-f1'
    Macro_F1 = 'macro-f1'
    Micro_F1 = 'micro-f1'
    PRECISION = 'precision'
    RECALL = 'recall'
    PSNR = 'psnr'
    SSIM = 'ssim'
    LPIPS = 'lpips'
    NIQE = 'niqe'
    AVERAGE_LOSS = 'avg_loss'
    FScore = 'fscore'
    FID = 'fid'
    BLEU_1 = 'bleu-1'
    BLEU_4 = 'bleu-4'
    ROUGE_1 = 'rouge-1'
    ROUGE_L = 'rouge-l'
    NED = 'ned'  # ocr metric
    mAP = 'mAP'
    BatchAcc = 'inbatch_t2i_recall_at_1'
    CROPPING_RATIO = 'cropping_ratio'
    DISTORTION_VALUE = 'distortion_value'
    STABILITY_SCORE = 'stability_score'
    PPL = 'ppl'
    PLCC = 'plcc'
    SRCC = 'srcc'
    RMSE = 'rmse'
    MRR = 'mrr'
    NDCG = 'ndcg'
    AR = 'AR'
    Colorfulness = 'colorfulness'
    Kendall_Tau_Correlation = 'kendall_tau_correlation'


class Metrics(object):
    """ Names for different metrics.
    """

    # accuracy
    accuracy = 'accuracy'

    multi_average_precision = 'mAP'
    audio_noise_metric = 'audio-noise-metric'
    PPL = 'ppl'

    # text gen
    BLEU = 'bleu'

    # metrics for image denoise task
    image_denoise_metric = 'image-denoise-metric'
    # metrics for video frame-interpolation task
    video_frame_interpolation_metric = 'video-frame-interpolation-metric'
    # metrics for real-world video super-resolution task
    video_super_resolution_metric = 'video-super-resolution-metric'

    # metric for image instance segmentation task
    image_ins_seg_coco_metric = 'image-ins-seg-coco-metric'
    # metrics for sequence classification task
    seq_cls_metric = 'seq-cls-metric'
    # loss metric
    loss_metric = 'loss-metric'
    # metrics for token-classification task
    token_cls_metric = 'token-cls-metric'
    # metrics for text-generation task
    text_gen_metric = 'text-gen-metric'
    # file saving wrapper
    prediction_saving_wrapper = 'prediction-saving-wrapper'
    # metrics for image-color-enhance task
    image_color_enhance_metric = 'image-color-enhance-metric'
    # metrics for image-portrait-enhancement task
    image_portrait_enhancement_metric = 'image-portrait-enhancement-metric'
    video_summarization_metric = 'video-summarization-metric'
    # metric for movie-scene-segmentation task
    movie_scene_segmentation_metric = 'movie-scene-segmentation-metric'
    # metric for inpainting task
    image_inpainting_metric = 'image-inpainting-metric'
    # metric for ocr
    NED = 'ned'
    # metric for cross-modal retrieval
    inbatch_recall = 'inbatch_recall'
    # metric for referring-video-object-segmentation task
    referring_video_object_segmentation_metric = 'referring-video-object-segmentation-metric'
    # metric for video stabilization task
    video_stabilization_metric = 'video-stabilization-metric'
    # metirc for image-quality-assessment-mos task
    image_quality_assessment_mos_metric = 'image-quality-assessment-mos-metric'
    # metirc for image-quality-assessment-degradation task
    image_quality_assessment_degradation_metric = 'image-quality-assessment-degradation-metric'
    # metric for text-ranking task
    text_ranking_metric = 'text-ranking-metric'
    # metric for image-colorization task
    image_colorization_metric = 'image-colorization-metric'
    ocr_recognition_metric = 'ocr-recognition-metric'
    # metric for translation evaluation
    translation_evaluation_metric = 'translation-evaluation-metric'


# ############################################ Dataset ############################################
class CVDatasets(object):
    # ocr
    icdar2015_ocr_detection = "icdar2015_ocr_detection"


class NLPDatasets(object):
    # text classification
    jd_sentiment_text_classification = "jd_sentiment_text_classification"


class Datasets(CVDatasets, NLPDatasets):
    """
    用于注册模块,module_name
    """

    reverse_field_index = {}
    dataset_template = 'task-template'

    @staticmethod
    def find_field_by_dataset(dataset_name):
        if len(Datasets.reverse_field_index) == 0:
            # Lazy init, not thread safe
            field_dict = {
                Fields.cv: [
                    getattr(Datasets, attr) for attr in dir(CVDatasets)
                    if not attr.startswith('__')
                ],
                Fields.nlp: [
                    getattr(Datasets, attr) for attr in dir(NLPDatasets)
                    if not attr.startswith('__')
                ],
                # Fields.audio: [
                #     getattr(Datasets, attr) for attr in dir(AudioDatasets)
                #     if not attr.startswith('__')
                # ],
                # Fields.multi_modal: [
                #     getattr(Datasets, attr) for attr in dir(MultiModalDatasets)
                #     if not attr.startswith('__')
                # ],
                # Fields.science: [
                #     getattr(Datasets, attr) for attr in dir(ScienceDatasets)
                #     if not attr.startswith('__')
                # ],
            }

            for field, datasets in field_dict.items():
                for dataset in datasets:
                    if dataset in Datasets.reverse_field_index:
                        raise ValueError(f'Duplicate dataset: {dataset}')
                    Datasets.reverse_field_index[dataset] = field

        return Datasets.reverse_field_index.get(dataset_name)


# ############################################ Task ############################################
class CVTasks(object):
    # ocr
    ocr_detection = 'ocr-detection'
    ocr_recognition = 'ocr-recognition'
    table_recognition = 'table-recognition'
    lineless_table_recognition = 'lineless-table-recognition'
    license_plate_detection = 'license-plate-detection'

    # human face body related
    animal_recognition = 'animal-recognition'
    face_detection = 'face-detection'
    face_liveness = 'face-liveness'
    face_quality_assessment = 'face-quality-assessment'
    card_detection = 'card-detection'
    face_recognition = 'face-recognition'
    facial_expression_recognition = 'facial-expression-recognition'
    face_processing_base = 'face-processing-base'
    face_attribute_recognition = 'face-attribute-recognition'
    face_2d_keypoints = 'face-2d-keypoints'
    human_detection = 'human-detection'
    human_object_interaction = 'human-object-interaction'
    face_image_generation = 'face-image-generation'
    body_2d_keypoints = 'body-2d-keypoints'
    body_3d_keypoints = 'body-3d-keypoints'
    hand_2d_keypoints = 'hand-2d-keypoints'
    general_recognition = 'general-recognition'
    human_wholebody_keypoint = 'human-wholebody-keypoint'
    pedestrian_attribute_recognition = 'pedestrian-attribute-recognition'

    image_classification = 'image-classification'
    image_multilabel_classification = 'image-multilabel-classification'
    image_classification_imagenet = 'image-classification-imagenet'
    image_classification_dailylife = 'image-classification-dailylife'

    image_object_detection = 'image-object-detection'
    video_object_detection = 'video-object-detection'
    image_fewshot_detection = 'image-fewshot-detection'
    open_vocabulary_detection = 'open-vocabulary-detection'
    object_detection_3d = 'object-detection-3d'

    image_segmentation = 'image-segmentation'
    semantic_segmentation = 'semantic-segmentation'
    image_driving_perception = 'image-driving-perception'
    image_depth_estimation = 'image-depth-estimation'
    indoor_layout_estimation = 'indoor-layout-estimation'
    video_depth_estimation = 'video-depth-estimation'
    panorama_depth_estimation = 'panorama-depth-estimation'
    portrait_matting = 'portrait-matting'
    universal_matting = 'universal-matting'
    text_driven_segmentation = 'text-driven-segmentation'
    shop_segmentation = 'shop-segmentation'
    hand_static = 'hand-static'
    face_human_hand_detection = 'face-human-hand-detection'
    face_emotion = 'face-emotion'
    product_segmentation = 'product-segmentation'
    image_matching = 'image-matching'
    image_quality_assessment_degradation = 'image-quality-assessment-degradation'

    crowd_counting = 'crowd-counting'

    # image editing
    skin_retouching = 'skin-retouching'
    image_super_resolution = 'image-super-resolution'
    image_debanding = 'image-debanding'
    image_colorization = 'image-colorization'
    image_color_enhancement = 'image-color-enhancement'
    image_denoising = 'image-denoising'
    image_deblurring = 'image-deblurring'
    image_portrait_enhancement = 'image-portrait-enhancement'
    image_inpainting = 'image-inpainting'
    image_paintbyexample = 'image-paintbyexample'
    image_skychange = 'image-skychange'
    image_demoireing = 'image-demoireing'

    # image generation
    image_to_image_translation = 'image-to-image-translation'
    image_to_image_generation = 'image-to-image-generation'
    image_style_transfer = 'image-style-transfer'
    image_portrait_stylization = 'image-portrait-stylization'
    image_body_reshaping = 'image-body-reshaping'
    image_embedding = 'image-embedding'
    image_face_fusion = 'image-face-fusion'
    product_retrieval_embedding = 'product-retrieval-embedding'
    controllable_image_generation = 'controllable-image-generation'

    # video recognition
    live_category = 'live-category'
    action_recognition = 'action-recognition'
    action_detection = 'action-detection'
    video_category = 'video-category'
    video_embedding = 'video-embedding'
    virtual_try_on = 'virtual-try-on'
    movie_scene_segmentation = 'movie-scene-segmentation'
    language_guided_video_summarization = 'language-guided-video-summarization'
    vop_retrieval = 'video-text-retrieval'

    # video segmentation
    video_object_segmentation = 'video-object-segmentation'
    referring_video_object_segmentation = 'referring-video-object-segmentation'
    video_human_matting = 'video-human-matting'
    video_panoptic_segmentation = 'video-panoptic-segmentation'
    video_instance_segmentation = 'video-instance-segmentation'

    # video editing
    video_inpainting = 'video-inpainting'
    video_frame_interpolation = 'video-frame-interpolation'
    video_stabilization = 'video-stabilization'
    video_super_resolution = 'video-super-resolution'
    video_deinterlace = 'video-deinterlace'
    video_colorization = 'video-colorization'

    # reid and tracking
    video_single_object_tracking = 'video-single-object-tracking'
    video_multi_object_tracking = 'video-multi-object-tracking'
    video_summarization = 'video-summarization'
    image_reid_person = 'image-reid-person'

    # pointcloud task
    pointcloud_sceneflow_estimation = 'pointcloud-sceneflow-estimation'
    # image multi-view depth estimation
    image_multi_view_depth_estimation = 'image-multi-view-depth-estimation'

    # domain specific object detection
    domain_specific_object_detection = 'domain-specific-object-detection'

    # content check
    content_check = 'content-check'

    # 3d face reconstruction
    face_reconstruction = 'face-reconstruction'

    # 3d human reconstruction
    human_reconstruction = 'human-reconstruction'

    # image quality assessment mos
    image_quality_assessment_mos = 'image-quality-assessment-mos'
    # motion generation
    motion_generation = 'motion-generation'
    # 3d reconstruction
    nerf_recon_acc = 'nerf-recon-acc'

    # vision efficient tuning
    vision_efficient_tuning = 'vision-efficient-tuning'

    # bad image detecting
    bad_image_detecting = 'bad-image-detecting'


class NLPTasks(object):
    # chat
    chat = 'chat'
    # nlp tasks
    word_segmentation = 'word-segmentation'
    part_of_speech = 'part-of-speech'
    named_entity_recognition = 'named-entity-recognition'
    nli = 'nli'
    sentiment_classification = 'sentiment-classification'
    sentiment_analysis = 'sentiment-analysis'
    sentence_similarity = 'sentence-similarity'
    text_classification = 'text-classification'
    sentence_embedding = 'sentence-embedding'
    text_ranking = 'text-ranking'
    relation_extraction = 'relation-extraction'
    zero_shot = 'zero-shot'
    translation = 'translation'
    competency_aware_translation = 'competency-aware-translation'
    token_classification = 'token-classification'
    transformer_crf = 'transformer-crf'
    conversational = 'conversational'
    text_generation = 'text-generation'
    fid_dialogue = 'fid-dialogue'
    text2text_generation = 'text2text-generation'
    task_oriented_conversation = 'task-oriented-conversation'
    dialog_intent_prediction = 'dialog-intent-prediction'
    dialog_state_tracking = 'dialog-state-tracking'
    table_question_answering = 'table-question-answering'
    fill_mask = 'fill-mask'
    text_summarization = 'text-summarization'
    question_answering = 'question-answering'
    code_translation = 'code-translation'
    code_generation = 'code-generation'
    zero_shot_classification = 'zero-shot-classification'
    backbone = 'backbone'
    text_error_correction = 'text-error-correction'
    word_alignment = 'word-alignment'
    faq_question_answering = 'faq-question-answering'
    information_extraction = 'information-extraction'
    document_segmentation = 'document-segmentation'
    extractive_summarization = 'extractive-summarization'
    feature_extraction = 'feature-extraction'
    translation_evaluation = 'translation-evaluation'
    sudoku = 'sudoku'
    text2sql = 'text2sql'
    siamese_uie = 'siamese-uie'
    document_grounded_dialog_retrieval = 'document-grounded-dialog-retrieval'
    document_grounded_dialog_rerank = 'document-grounded-dialog-rerank'
    document_grounded_dialog_generate = 'document-grounded-dialog-generate'


class AudioTasks(object):
    # audio tasks
    auto_speech_recognition = 'auto-speech-recognition'
    text_to_speech = 'text-to-speech'
    speech_signal_process = 'speech-signal-process'
    speech_separation = 'speech-separation'
    acoustic_echo_cancellation = 'acoustic-echo-cancellation'
    acoustic_noise_suppression = 'acoustic-noise-suppression'
    keyword_spotting = 'keyword-spotting'
    inverse_text_processing = 'inverse-text-processing'
    punctuation = 'punctuation'
    speaker_verification = 'speaker-verification'
    speaker_diarization = 'speaker-diarization'
    voice_activity_detection = 'voice-activity-detection'
    language_score_prediction = 'language-score-prediction'
    speech_timestamp = 'speech-timestamp'


class MultiModalTasks(object):
    # multi-modal tasks
    image_captioning = 'image-captioning'
    visual_grounding = 'visual-grounding'
    text_to_image_synthesis = 'text-to-image-synthesis'
    multi_modal_embedding = 'multi-modal-embedding'
    generative_multi_modal_embedding = 'generative-multi-modal-embedding'
    multi_modal_similarity = 'multi-modal-similarity'
    visual_question_answering = 'visual-question-answering'
    visual_entailment = 'visual-entailment'
    video_multi_modal_embedding = 'video-multi-modal-embedding'
    image_text_retrieval = 'image-text-retrieval'
    document_vl_embedding = 'document-vl-embedding'
    video_captioning = 'video-captioning'
    video_question_answering = 'video-question-answering'
    video_temporal_grounding = 'video-temporal-grounding'
    text_to_video_synthesis = 'text-to-video-synthesis'
    efficient_diffusion_tuning = 'efficient-diffusion-tuning'
    multimodal_dialogue = 'multimodal-dialogue'


class ScienceTasks(object):
    protein_structure = 'protein-structure'


class TasksIODescriptions(object):
    image_to_image = 'image_to_image',
    images_to_image = 'images_to_image',
    image_to_text = 'image_to_text',
    seed_to_image = 'seed_to_image',
    text_to_speech = 'text_to_speech',
    text_to_text = 'text_to_text',
    speech_to_text = 'speech_to_text',
    speech_to_speech = 'speech_to_speech'
    speeches_to_speech = 'speeches_to_speech',
    visual_grounding = 'visual_grounding',
    visual_question_answering = 'visual_question_answering',
    visual_entailment = 'visual_entailment',
    generative_multi_modal_embedding = 'generative_multi_modal_embedding'
    efficient_diffusion_tuning = 'efficient_diffusion_tuning'


class Tasks(CVTasks, NLPTasks, AudioTasks, MultiModalTasks, ScienceTasks):
    """ Names for tasks supported by modelscope.

    Holds the standard task name to use for identifying different tasks.
    This should be used to register models, pipelines, trainers.
    """
    reverse_field_index = {}
    task_template = 'task-template'

    @staticmethod
    def find_field_by_task(task_name):
        if len(Tasks.reverse_field_index) == 0:
            # Lazy init, not thread safe
            field_dict = {
                Fields.cv: [
                    getattr(Tasks, attr) for attr in dir(CVTasks)
                    if not attr.startswith('__')
                ],
                Fields.nlp: [
                    getattr(Tasks, attr) for attr in dir(NLPTasks)
                    if not attr.startswith('__')
                ],
                Fields.audio: [
                    getattr(Tasks, attr) for attr in dir(AudioTasks)
                    if not attr.startswith('__')
                ],
                Fields.multi_modal: [
                    getattr(Tasks, attr) for attr in dir(MultiModalTasks)
                    if not attr.startswith('__')
                ],
                Fields.science: [
                    getattr(Tasks, attr) for attr in dir(ScienceTasks)
                    if not attr.startswith('__')
                ],
            }

            for field, tasks in field_dict.items():
                for task in tasks:
                    if task in Tasks.reverse_field_index:
                        raise ValueError(f'Duplicate task: {task}')
                    Tasks.reverse_field_index[task] = field

        return Tasks.reverse_field_index.get(task_name)


# ############################################ Trainer ############################################


class CVTrainers(object):
    # cv trainers
    image_instance_segmentation = 'image-instance-segmentation'
    image_portrait_enhancement = 'image-portrait-enhancement'
    video_summarization = 'video-summarization'
    movie_scene_segmentation = 'movie-scene-segmentation'
    face_detection_scrfd = 'face-detection-scrfd'
    card_detection_scrfd = 'card-detection-scrfd'
    image_inpainting = 'image-inpainting'
    referring_video_object_segmentation = 'referring-video-object-segmentation'
    image_classification_team = 'image-classification-team'
    image_classification = 'image-classification'
    image_fewshot_detection = 'image-fewshot-detection'
    ocr_recognition = 'ocr-recognition'
    ocr_detection_db = 'ocr-detection-db'
    nerf_recon_acc = 'nerf-recon-acc'
    action_detection = 'action-detection'
    vision_efficient_tuning = 'vision-efficient-tuning'


class NLPTrainers(object):
    # nlp trainers
    bert_sentiment_analysis = 'bert-sentiment-analysis'
    dialog_modeling_trainer = 'dialog-modeling-trainers'
    dialog_intent_trainer = 'dialog-intent-trainers'
    nlp_base_trainer = 'nlp-base-trainers'
    nlp_veco_trainer = 'nlp-veco-trainers'
    nlp_text_ranking_trainer = 'nlp-text-ranking-trainers'
    nlp_sentence_embedding_trainer = 'nlp-sentence-embedding-trainers'
    text_generation_trainer = 'text-generation-trainers'
    nlp_plug_trainer = 'nlp-plug-trainers'
    gpt3_trainer = 'nlp-gpt3-trainers'
    faq_question_answering_trainer = 'faq-question-answering-trainers'
    gpt_moe_trainer = 'nlp-gpt-moe-trainers'
    table_question_answering_trainer = 'table-question-answering-trainers'
    document_grounded_dialog_generate_trainer = 'document-grounded-dialog-generate-trainers'
    document_grounded_dialog_rerank_trainer = 'document-grounded-dialog-rerank-trainers'
    document_grounded_dialog_retrieval_trainer = 'document-grounded-dialog-retrieval-trainers'
    siamese_uie_trainer = 'siamese-uie-trainers'
    translation_evaluation_trainer = 'translation-evaluation-trainers'


class MultiModalTrainers(object):
    clip_multi_modal_embedding = 'clip-multi-modal-embedding'
    ofa = 'ofa'
    mplug = 'mplug'
    mgeo_ranking_trainer = 'mgeo-ranking-trainers'
    efficient_diffusion_tuning = 'efficient-diffusion-tuning'


class AudioTrainers(object):
    speech_frcrn_ans_cirm_16k = 'speech_frcrn_ans_cirm_16k'
    speech_dfsmn_kws_char_farfield = 'speech_dfsmn_kws_char_farfield'
    speech_kws_fsmn_char_ctc_nearfield = 'speech_kws_fsmn_char_ctc_nearfield'
    speech_kantts_trainer = 'speech-kantts-trainers'
    speech_asr_trainer = 'speech-asr-trainers'
    speech_separation = 'speech-separation'


class Trainers(CVTrainers, NLPTrainers, MultiModalTrainers, AudioTrainers):
    """ Names for different trainers.

        Holds the standard trainers name to use for identifying different trainers.
    This should be used to register trainers.

        For a general Trainer, you can use EpochBasedTrainer.
        For a model specific Trainer, you can use ${ModelName}-${Task}-trainers.
    """

    default = 'trainers'
    tinynas_damoyolo = 'tinynas-damoyolo'

    @staticmethod
    def get_trainer_domain(attribute_or_value):
        if attribute_or_value in vars(
                CVTrainers) or attribute_or_value in vars(CVTrainers).values():
            return Fields.cv
        elif attribute_or_value in vars(
                NLPTrainers) or attribute_or_value in vars(
            NLPTrainers).values():
            return Fields.nlp
        elif attribute_or_value in vars(
                AudioTrainers) or attribute_or_value in vars(
            AudioTrainers).values():
            return Fields.audio
        elif attribute_or_value in vars(
                MultiModalTrainers) or attribute_or_value in vars(
            MultiModalTrainers).values():
            return Fields.multi_modal
        elif attribute_or_value == Trainers.default:
            return Trainers.default
        else:
            return 'unknown'


# ############################################ Preprocessor ############################################
class Preprocessors(object):
    """ Names for different preprocessor.

        Holds the standard preprocessor name to use for identifying different preprocessor.
    This should be used to register preprocessors.

        For a general preprocessor, just use the function name as preprocessor name such as
    resize-image, random-crop
        For a model-specific preprocessor, use ${modelname}-${fuction}
    """

    # cv preprocessor
    load_image = 'load-image'
    image_denoise_preprocessor = 'image-denoise-preprocessor'
    image_deblur_preprocessor = 'image-deblur-preprocessor'
    object_detection_tinynas_preprocessor = 'object-detection-tinynas-preprocessor'
    image_classification_mmcv_preprocessor = 'image-classification-mmcv-preprocessor'
    image_color_enhance_preprocessor = 'image-color-enhance-preprocessor'
    image_instance_segmentation_preprocessor = 'image-instance-segmentation-preprocessor'
    image_driving_perception_preprocessor = 'image-driving-perception-preprocessor'
    image_portrait_enhancement_preprocessor = 'image-portrait-enhancement-preprocessor'
    image_quality_assessment_man_preprocessor = 'image-quality_assessment-man-preprocessor'
    image_quality_assessment_mos_preprocessor = 'image-quality_assessment-mos-preprocessor'
    video_summarization_preprocessor = 'video-summarization-preprocessor'
    movie_scene_segmentation_preprocessor = 'movie-scene-segmentation-preprocessor'
    image_classification_bypass_preprocessor = 'image-classification-bypass-preprocessor'
    object_detection_scrfd = 'object-detection-scrfd'
    image_sky_change_preprocessor = 'image-sky-change-preprocessor'
    image_demoire_preprocessor = 'image-demoire-preprocessor'
    ocr_recognition = 'ocr-recognition'
    ocr_detection = 'ocr-detection'
    bad_image_detecting_preprocessor = 'bad-image-detecting-preprocessor'
    nerf_recon_acc_preprocessor = 'nerf-recon-acc-preprocessor'
    controllable_image_generation_preprocessor = 'controllable-image-generation-preprocessor'
    image_classification_preprocessor = 'image-classification-preprocessor'

    # nlp preprocessor
    sen_sim_tokenizer = 'sen-sim-tokenizer'
    cross_encoder_tokenizer = 'cross-encoder-tokenizer'
    bert_seq_cls_tokenizer = 'bert-seq-cls-tokenizer'
    text_gen_tokenizer = 'text-gen-tokenizer'
    text2text_gen_preprocessor = 'text2text-gen-preprocessor'
    text_gen_jieba_tokenizer = 'text-gen-jieba-tokenizer'
    text2text_translate_preprocessor = 'text2text-translate-preprocessor'
    token_cls_tokenizer = 'token-cls-tokenizer'
    ner_tokenizer = 'ner-tokenizer'
    thai_ner_tokenizer = 'thai-ner-tokenizer'
    viet_ner_tokenizer = 'viet-ner-tokenizer'
    nli_tokenizer = 'nli-tokenizer'
    sen_cls_tokenizer = 'sen-cls-tokenizer'
    dialog_intent_preprocessor = 'dialog-intent-preprocessor'
    dialog_modeling_preprocessor = 'dialog-modeling-preprocessor'
    dialog_state_tracking_preprocessor = 'dialog-state-tracking-preprocessor'
    sbert_token_cls_tokenizer = 'sbert-token-cls-tokenizer'
    zero_shot_cls_tokenizer = 'zero-shot-cls-tokenizer'
    text_error_correction = 'text-error-correction'
    word_alignment = 'word-alignment'
    sentence_embedding = 'sentence-embedding'
    text_ranking = 'text-ranking'
    sequence_labeling_tokenizer = 'sequence-labeling-tokenizer'
    word_segment_text_to_label_preprocessor = 'word-segment-text-to-label-preprocessor'
    thai_wseg_tokenizer = 'thai-wseg-tokenizer'
    fill_mask = 'fill-mask'
    fill_mask_ponet = 'fill-mask-ponet'
    faq_question_answering_preprocessor = 'faq-question-answering-preprocessor'
    conversational_text_to_sql = 'conversational-text-to-sql'
    table_question_answering_preprocessor = 'table-question-answering-preprocessor'
    re_tokenizer = 're-tokenizer'
    document_segmentation = 'document-segmentation'
    feature_extraction = 'feature-extraction'
    mglm_summarization = 'mglm-summarization'
    sentence_piece = 'sentence-piece'
    translation_evaluation = 'translation-evaluation-preprocessor'
    canmt_translation = 'canmt-translation'
    dialog_use_preprocessor = 'dialog-use-preprocessor'
    siamese_uie_preprocessor = 'siamese-uie-preprocessor'
    document_grounded_dialog_retrieval = 'document-grounded-dialog-retrieval'
    document_grounded_dialog_rerank = 'document-grounded-dialog-rerank'
    document_grounded_dialog_generate = 'document-grounded-dialog-generate'

    # audio preprocessor
    linear_aec_fbank = 'linear-aec-fbank'
    text_to_tacotron_symbols = 'text-to-tacotron-symbols'
    wav_to_lists = 'wav-to-lists'
    wav_to_scp = 'wav-to-scp'
    kantts_data_preprocessor = 'kantts-data-preprocessor'

    # multi-modal preprocessor
    ofa_tasks_preprocessor = 'ofa-tasks-preprocessor'
    clip_preprocessor = 'clip-preprocessor'
    mplug_tasks_preprocessor = 'mplug-tasks-preprocessor'
    mgeo_ranking = 'mgeo-ranking'
    vldoc_preprocessor = 'vldoc-preprocessor'
    hitea_tasks_preprocessor = 'hitea-tasks-preprocessor'
    diffusion_image_generation_preprocessor = 'diffusion-image-generation-preprocessor'
    mplug_owl_preprocessor = 'mplug-owl-preprocessor'
    image_captioning_clip_interrogator_preprocessor = 'image-captioning-clip-interrogator-preprocessor'

    # science preprocessor
    unifold_preprocessor = 'unifold-preprocessor'


# ############################################ Optimizers ############################################
class Optimizers(object):
    """ Names for different OPTIMIZER.

        Holds the standard optimizer name to use for identifying different optimizer.
        This should be used to register optimizer.
    """

    default = 'optimizer'

    SGD = 'SGD'


# ############################################ LR_Schedulers ############################################
class LR_Schedulers(object):
    """learning rate scheduler is defined here

    """
    LinearWarmup = 'LinearWarmup'
    ConstantWarmup = 'ConstantWarmup'
    ExponentialWarmup = 'ExponentialWarmup'


# ############################################ TaskModels ############################################
class TaskModels(object):
    # nlp task
    text_classification = 'text-classification'
    token_classification = 'token-classification'
    information_extraction = 'information-extraction'
    fill_mask = 'fill-mask'
    feature_extraction = 'feature-extraction'
    text_generation = 'text-generation'
    text_ranking = 'text-ranking'

# ############################################ Heads ############################################
class Heads(object):
    # nlp heads

    # text cls
    text_classification = 'text-classification'
    # fill mask
    fill_mask = 'fill-mask'
    bert_mlm = 'bert-mlm'
    roberta_mlm = 'roberta-mlm'
    xlm_roberta_mlm = 'xlm-roberta-mlm'
    # token cls
    token_classification = 'token-classification'
    # extraction
    information_extraction = 'information-extraction'
    # text gen
    text_generation = 'text-generation'
    # text ranking
    text_ranking = 'text-ranking'
    # crf
    lstm_crf = 'lstm-crf'
    transformer_crf = 'transformer-crf'




class Models(object):
    """ Names for different models.

        Holds the standard model name to use for identifying different model.
    This should be used to register models.

        Model name should only contain model information but not task information.
    """
    # tinynas models
    tinynas_detection = 'tinynas-detection'
    tinynas_damoyolo = 'tinynas-damoyolo'
    # vision models
    detection = 'detection'
    mask_scoring = 'MaskScoring'
    image_restoration = 'image-restoration'
    realtime_object_detection = 'realtime-object-detection'
    realtime_video_object_detection = 'realtime-video-object-detection'
    scrfd = 'scrfd'
    depe = 'depe'
    classification_model = 'ClassificationModel'
    easyrobust_model = 'EasyRobustModel'
    bnext = 'bnext'
    yolopv2 = 'yolopv2'
    nafnet = 'nafnet'
    csrnet = 'csrnet'
    adaint = 'adaint'
    deeplpfnet = 'deeplpfnet'
    rrdb = 'rrdb'
    cascade_mask_rcnn_swin = 'cascade_mask_rcnn_swin'
    maskdino_swin = 'maskdino_swin'
    gpen = 'gpen'
    product_retrieval_embedding = 'product-retrieval-embedding'
    body_2d_keypoints = 'body-2d-keypoints'
    body_3d_keypoints = 'body-3d-keypoints'
    body_3d_keypoints_hdformer = 'hdformer'
    crowd_counting = 'HRNetCrowdCounting'
    face_2d_keypoints = 'face-2d-keypoints'
    panoptic_segmentation = 'swinL-panoptic-segmentation'
    r50_panoptic_segmentation = 'r50-panoptic-segmentation'
    image_reid_person = 'passvitb'
    image_inpainting = 'FFTInpainting'
    image_paintbyexample = 'Stablediffusion-Paintbyexample'
    video_summarization = 'pgl-video-summarization'
    video_panoptic_segmentation = 'swinb-video-panoptic-segmentation'
    video_instance_segmentation = 'swinb-video-instance-segmentation'
    language_guided_video_summarization = 'clip-it-language-guided-video-summarization'
    swinL_semantic_segmentation = 'swinL-semantic-segmentation'
    vitadapter_semantic_segmentation = 'vitadapter-semantic-segmentation'
    text_driven_segmentation = 'text-driven-segmentation'
    newcrfs_depth_estimation = 'newcrfs-depth-estimation'
    panovit_layout_estimation = 'panovit-layout-estimation'
    unifuse_depth_estimation = 'unifuse-depth-estimation'
    dro_resnet18_depth_estimation = 'dro-resnet18-depth-estimation'
    resnet50_bert = 'resnet50-bert'
    referring_video_object_segmentation = 'swinT-referring-video-object-segmentation'
    fer = 'fer'
    fairface = 'fairface'
    retinaface = 'retinaface'
    damofd = 'damofd'
    shop_segmentation = 'shop-segmentation'
    mogface = 'mogface'
    mtcnn = 'mtcnn'
    ulfd = 'ulfd'
    rts = 'rts'
    flir = 'flir'
    arcface = 'arcface'
    facemask = 'facemask'
    flc = 'flc'
    tinymog = 'tinymog'
    video_inpainting = 'video-inpainting'
    human_wholebody_keypoint = 'human-wholebody-keypoint'
    hand_static = 'hand-static'
    face_human_hand_detection = 'face-human-hand-detection'
    face_emotion = 'face-emotion'
    product_segmentation = 'product-segmentation'
    image_body_reshaping = 'image-body-reshaping'
    image_skychange = 'image-skychange'
    video_human_matting = 'video-human-matting'
    human_reconstruction = 'human-reconstruction'
    video_frame_interpolation = 'video-frame-interpolation'
    video_object_segmentation = 'video-object-segmentation'
    video_deinterlace = 'video-deinterlace'
    quadtree_attention_image_matching = 'quadtree-attention-image-matching'
    vision_middleware = 'vision-middleware'
    vidt = 'vidt'
    video_stabilization = 'video-stabilization'
    real_basicvsr = 'real-basicvsr'
    rcp_sceneflow_estimation = 'rcp-sceneflow-estimation'
    image_casmvs_depth_estimation = 'image-casmvs-depth-estimation'
    vop_retrieval_model = 'vop-retrieval-model'
    vop_retrieval_model_se = 'vop-retrieval-model-se'
    ddcolor = 'ddcolor'
    image_probing_model = 'image-probing-model'
    defrcn = 'defrcn'
    image_face_fusion = 'image-face-fusion'
    content_check = 'content-check'
    open_vocabulary_detection_vild = 'open-vocabulary-detection-vild'
    ecbsr = 'ecbsr'
    msrresnet_lite = 'msrresnet-lite'
    object_detection_3d = 'object_detection_3d'
    ddpm = 'ddpm'
    ocr_recognition = 'OCRRecognition'
    ocr_detection = 'OCRDetection'
    lineless_table_recognition = 'LoreModel'
    image_quality_assessment_mos = 'image-quality-assessment-mos'
    image_quality_assessment_man = 'image-quality-assessment-man'
    image_quality_assessment_degradation = 'image-quality-assessment-degradation'
    m2fp = 'm2fp'
    nerf_recon_acc = 'nerf-recon-acc'
    bts_depth_estimation = 'bts-depth-estimation'
    vision_efficient_tuning = 'vision-efficient-tuning'
    bad_image_detecting = 'bad-image-detecting'
    controllable_image_generation = 'controllable-image-generation'
    longshortnet = 'longshortnet'
    fastinst = 'fastinst'
    pedestrian_attribute_recognition = 'pedestrian-attribute-recognition'

    # nlp models
    bert = 'bert'
    palm = 'palm-v2'
    structbert = 'structbert'
    deberta_v2 = 'deberta_v2'
    veco = 'veco'
    translation = 'csanmt-translation'
    canmt = 'canmt'
    space_dst = 'space-dst'
    space_intent = 'space-intent'
    space_modeling = 'space-modeling'
    space_T_en = 'space-T-en'
    space_T_cn = 'space-T-cn'
    tcrf = 'transformer-crf'
    token_classification_for_ner = 'token-classification-for-ner'
    tcrf_wseg = 'transformer-crf-for-word-segmentation'
    transformer_softmax = 'transformer-softmax'
    lcrf = 'lstm-crf'
    lcrf_wseg = 'lstm-crf-for-word-segmentation'
    gcnncrf = 'gcnn-crf'
    bart = 'bart'
    gpt2 = 'gpt2'
    gpt3 = 'gpt3'
    gpt_moe = 'gpt-moe'
    gpt_neo = 'gpt-neo'
    plug = 'plug'
    bert_for_ds = 'bert-for-document-segmentation'
    ponet_for_ds = 'ponet-for-document-segmentation'
    ponet = 'ponet'
    T5 = 'T5'
    mglm = 'mglm'
    codegeex = 'codegeex'
    glm130b = 'glm130b'
    bloom = 'bloom'
    unite = 'unite'
    megatron_bert = 'megatron-bert'
    use = 'user-satisfaction-estimation'
    fid_plug = 'fid-plug'
    fid_T5 = 'fid-T5'
    lstm = 'lstm'
    xlm_roberta = 'xlm-roberta'
    transformers = 'transformers'
    plug_mental = 'plug-mental'
    doc2bot = 'doc2bot'
    peer = 'peer'
    llama = 'llama'

    # audio models
    sambert_hifigan = 'sambert-hifigan'
    speech_frcrn_ans_cirm_16k = 'speech_frcrn_ans_cirm_16k'
    speech_dfsmn_ans = 'speech_dfsmn_ans'
    speech_dfsmn_kws_char_farfield = 'speech_dfsmn_kws_char_farfield'
    speech_dfsmn_kws_char_farfield_iot = 'speech_dfsmn_kws_char_farfield_iot'
    speech_kws_fsmn_char_ctc_nearfield = 'speech_kws_fsmn_char_ctc_nearfield'
    speech_mossformer_separation_temporal_8k = 'speech_mossformer_separation_temporal_8k'
    kws_kwsbp = 'kws-kwsbp'
    generic_asr = 'generic-asr'
    wenet_asr = 'wenet-asr'
    generic_itn = 'generic-itn'
    generic_punc = 'generic-punc'
    generic_sv = 'generic-sv'
    ecapa_tdnn_sv = 'ecapa-tdnn-sv'
    campplus_sv = 'cam++-sv'
    eres2net_sv = 'eres2net-sv'
    scl_sd = 'scl-sd'
    rdino_tdnn_sv = 'rdino_ecapa-tdnn-sv'
    generic_lm = 'generic-lm'

    # multi-modal models
    ofa = 'ofa'
    clip = 'clip-multi-modal-embedding'
    gemm = 'gemm-generative-multi-modal'
    rleg = 'rleg-generative-multi-modal'
    mplug = 'mplug'
    diffusion = 'diffusion-text-to-image-synthesis'
    multi_stage_diffusion = 'multi-stage-diffusion-text-to-image-synthesis'
    video_synthesis = 'latent-text-to-video-synthesis'
    team = 'team-multi-modal-similarity'
    video_clip = 'video-clip-multi-modal-embedding'
    mgeo = 'mgeo'
    vldoc = 'vldoc'
    hitea = 'hitea'
    soonet = 'soonet'
    efficient_diffusion_tuning = 'efficient-diffusion-tuning'
    mplug_owl = 'mplug-owl'
    clip_interrogator = 'clip-interrogator'

    # science models
    unifold = 'unifold'
    unifold_symmetry = 'unifold-symmetry'








class Pipelines(object):
    """ Names for different pipelines.

        Holds the standard pipline name to use for identifying different pipeline.
    This should be used to register pipelines.

        For pipeline which support different models and implements the common function, we
    should use task name for this pipeline.
        For pipeline which suuport only one model, we should use ${Model}-${Task} as its name.
    """
    pipeline_template = 'pipeline-template'
    # vision tasks
    portrait_matting = 'unet-image-matting'
    universal_matting = 'unet-universal-matting'
    image_denoise = 'nafnet-image-denoise'
    image_deblur = 'nafnet-image-deblur'
    person_image_cartoon = 'unet-person-image-cartoon'
    ocr_detection = 'resnet18-ocr-detection'
    table_recognition = 'dla34-table-recognition'
    lineless_table_recognition = 'lore-lineless-table-recognition'
    license_plate_detection = 'resnet18-license-plate-detection'
    action_recognition = 'TAdaConv_action-recognition'
    animal_recognition = 'resnet101-animal-recognition'
    general_recognition = 'resnet101-general-recognition'
    cmdssl_video_embedding = 'cmdssl-r2p1d_video_embedding'
    hicossl_video_embedding = 'hicossl-s3dg-video_embedding'
    body_2d_keypoints = 'hrnetv2w32_body-2d-keypoints_image'
    body_3d_keypoints = 'canonical_body-3d-keypoints_video'
    hand_2d_keypoints = 'hrnetv2w18_hand-2d-keypoints_image'
    human_detection = 'resnet18-human-detection'
    tbs_detection = 'tbs-detection'
    object_detection = 'vit-object-detection'
    abnormal_object_detection = 'abnormal-object-detection'
    face_2d_keypoints = 'mobilenet_face-2d-keypoints_alignment'
    salient_detection = 'u2net-salient-detection'
    salient_boudary_detection = 'res2net-salient-detection'
    camouflaged_detection = 'res2net-camouflaged-detection'
    image_demoire = 'uhdm-image-demoireing'
    image_classification = 'image-classification'
    face_detection = 'resnet-face-detection-scrfd10gkps'
    face_liveness_ir = 'manual-face-liveness-flir'
    face_liveness_rgb = 'manual-face-liveness-flir'
    face_liveness_xc = 'manual-face-liveness-flxc'
    card_detection = 'resnet-card-detection-scrfd34gkps'
    ulfd_face_detection = 'manual-face-detection-ulfd'
    tinymog_face_detection = 'manual-face-detection-tinymog'
    facial_expression_recognition = 'vgg19-facial-expression-recognition-fer'
    facial_landmark_confidence = 'manual-facial-landmark-confidence-flcm'
    face_attribute_recognition = 'resnet34-face-attribute-recognition-fairface'
    retina_face_detection = 'resnet50-face-detection-retinaface'
    mog_face_detection = 'resnet101-face-detection-cvpr22papermogface'
    mtcnn_face_detection = 'manual-face-detection-mtcnn'
    live_category = 'live-category'
    general_image_classification = 'vit-base_image-classification_ImageNet-labels'
    daily_image_classification = 'vit-base_image-classification_Dailylife-labels'
    nextvit_small_daily_image_classification = 'nextvit-small_image-classification_Dailylife-labels'
    convnext_base_image_classification_garbage = 'convnext-base_image-classification_garbage'
    bnext_small_image_classification = 'bnext-small_image-classification_ImageNet-labels'
    yolopv2_image_driving_percetion_bdd100k = 'yolopv2_image-driving-percetion_bdd100k'
    common_image_classification = 'common-image-classification'
    image_color_enhance = 'csrnet-image-color-enhance'
    adaint_image_color_enhance = 'adaint-image-color-enhance'
    deeplpf_image_color_enhance = 'deeplpf-image-color-enhance'
    virtual_try_on = 'virtual-try-on'
    image_colorization = 'unet-image-colorization'
    image_style_transfer = 'AAMS-style-transfer'
    image_super_resolution = 'rrdb-image-super-resolution'
    image_debanding = 'rrdb-image-debanding'
    face_image_generation = 'gan-face-image-generation'
    product_retrieval_embedding = 'resnet50-product-retrieval-embedding'
    realtime_video_object_detection = 'cspnet_realtime-video-object-detection_streamyolo'
    face_recognition = 'ir101-face-recognition-cfglint'
    face_recognition_ood = 'ir-face-recognition-ood-rts'
    face_quality_assessment = 'manual-face-quality-assessment-fqa'
    face_recognition_ood = 'ir-face-recognition-rts'
    face_recognition_onnx_ir = 'manual-face-recognition-frir'
    face_recognition_onnx_fm = 'manual-face-recognition-frfm'
    arc_face_recognition = 'ir50-face-recognition-arcface'
    mask_face_recognition = 'resnet-face-recognition-facemask'
    content_check = 'resnet50-image-classification-cc'
    image_instance_segmentation = 'cascade-mask-rcnn-swin-image-instance-segmentation'
    maskdino_instance_segmentation = 'maskdino-swin-image-instance-segmentation'
    image2image_translation = 'image-to-image-translation'
    live_category = 'live-category'
    video_category = 'video-category'
    ocr_recognition = 'convnextTiny-ocr-recognition'
    image_portrait_enhancement = 'gpen-image-portrait-enhancement'
    image_to_image_generation = 'image-to-image-generation'
    image_object_detection_auto = 'yolox_image-object-detection-auto'
    hand_detection = 'yolox-pai_hand-detection'
    skin_retouching = 'unet-skin-retouching'
    face_reconstruction = 'resnet50-face-reconstruction'
    tinynas_classification = 'tinynas-classification'
    easyrobust_classification = 'easyrobust-classification'
    tinynas_detection = 'tinynas-detection'
    crowd_counting = 'hrnet-crowd-counting'
    action_detection = 'ResNetC3D-action-detection'
    video_single_object_tracking = 'ostrack-vitb-video-single-object-tracking'
    video_single_object_tracking_procontext = 'procontext-vitb-video-single-object-tracking'
    video_multi_object_tracking = 'video-multi-object-tracking'
    image_panoptic_segmentation = 'image-panoptic-segmentation'
    video_summarization = 'googlenet_pgl_video_summarization'
    language_guided_video_summarization = 'clip-it-video-summarization'
    image_semantic_segmentation = 'image-semantic-segmentation'
    image_depth_estimation = 'image-depth-estimation'
    indoor_layout_estimation = 'indoor-layout-estimation'
    video_depth_estimation = 'video-depth-estimation'
    panorama_depth_estimation = 'panorama-depth-estimation'
    image_reid_person = 'passvitb-image-reid-person'
    image_inpainting = 'fft-inpainting'
    image_paintbyexample = 'stablediffusion-paintbyexample'
    image_inpainting_sdv2 = 'image-inpainting-sdv2'
    text_driven_segmentation = 'text-driven-segmentation'
    movie_scene_segmentation = 'resnet50-bert-movie-scene-segmentation'
    shop_segmentation = 'shop-segmentation'
    video_inpainting = 'video-inpainting'
    human_wholebody_keypoint = 'hrnetw48_human-wholebody-keypoint_image'
    pst_action_recognition = 'patchshift-action-recognition'
    hand_static = 'hand-static'
    face_human_hand_detection = 'face-human-hand-detection'
    face_emotion = 'face-emotion'
    product_segmentation = 'product-segmentation'
    image_body_reshaping = 'flow-based-body-reshaping'
    referring_video_object_segmentation = 'referring-video-object-segmentation'
    image_skychange = 'image-skychange'
    video_human_matting = 'video-human-matting'
    human_reconstruction = 'human-reconstruction'
    vision_middleware_multi_task = 'vision-middleware-multi-task'
    vidt = 'vidt'
    video_frame_interpolation = 'video-frame-interpolation'
    video_object_segmentation = 'video-object-segmentation'
    video_deinterlace = 'video-deinterlace'
    image_matching = 'image-matching'
    video_stabilization = 'video-stabilization'
    video_super_resolution = 'realbasicvsr-video-super-resolution'
    pointcloud_sceneflow_estimation = 'pointcloud-sceneflow-estimation'
    image_multi_view_depth_estimation = 'image-multi-view-depth-estimation'
    video_panoptic_segmentation = 'video-panoptic-segmentation'
    video_instance_segmentation = 'video-instance-segmentation'
    vop_retrieval = 'vop-video-text-retrieval'
    vop_retrieval_se = 'vop-video-text-retrieval-se'
    ddcolor_image_colorization = 'ddcolor-image-colorization'
    image_structured_model_probing = 'image-structured-model-probing'
    image_fewshot_detection = 'image-fewshot-detection'
    image_face_fusion = 'image-face-fusion'
    open_vocabulary_detection_vild = 'open-vocabulary-detection-vild'
    ddpm_image_semantic_segmentation = 'ddpm-image-semantic-segmentation'
    video_colorization = 'video-colorization'
    motion_generattion = 'mdm-motion-generation'
    mobile_image_super_resolution = 'mobile-image-super-resolution'
    image_human_parsing = 'm2fp-image-human-parsing'
    object_detection_3d_depe = 'object-detection-3d-depe'
    nerf_recon_acc = 'nerf-recon-acc'
    bad_image_detecting = 'bad-image-detecting'
    controllable_image_generation = 'controllable-image-generation'
    fast_instance_segmentation = 'fast-instance-segmentation'
    image_quality_assessment_mos = 'image-quality-assessment-mos'
    image_quality_assessment_man = 'image-quality-assessment-man'
    image_quality_assessment_degradation = 'image-quality-assessment-degradation'
    vision_efficient_tuning = 'vision-efficient-tuning'
    image_bts_depth_estimation = 'image-bts-depth-estimation'
    pedestrian_attribute_recognition = 'resnet50_pedestrian-attribute-recognition_image'

    # nlp tasks
    automatic_post_editing = 'automatic-post-editing'
    translation_quality_estimation = 'translation-quality-estimation'
    domain_classification = 'domain-classification'
    sentence_similarity = 'sentence-similarity'
    word_segmentation = 'word-segmentation'
    multilingual_word_segmentation = 'multilingual-word-segmentation'
    word_segmentation_thai = 'word-segmentation-thai'
    part_of_speech = 'part-of-speech'
    named_entity_recognition = 'named-entity-recognition'
    named_entity_recognition_thai = 'named-entity-recognition-thai'
    named_entity_recognition_viet = 'named-entity-recognition-viet'
    text_generation = 'text-generation'
    fid_dialogue = 'fid-dialogue'
    text2text_generation = 'text2text-generation'
    sentiment_analysis = 'sentiment-analysis'
    sentiment_classification = 'sentiment-classification'
    text_classification = 'text-classification'
    fill_mask = 'fill-mask'
    fill_mask_ponet = 'fill-mask-ponet'
    csanmt_translation = 'csanmt-translation'
    canmt_translation = 'canmt-translation'
    interactive_translation = 'interactive-translation'
    nli = 'nli'
    dialog_intent_prediction = 'dialog-intent-prediction'
    dialog_modeling = 'dialog-modeling'
    dialog_state_tracking = 'dialog-state-tracking'
    zero_shot_classification = 'zero-shot-classification'
    text_error_correction = 'text-error-correction'
    word_alignment = 'word-alignment'
    plug_generation = 'plug-generation'
    gpt3_generation = 'gpt3-generation'
    gpt_moe_generation = 'gpt-moe-generation'
    faq_question_answering = 'faq-question-answering'
    conversational_text_to_sql = 'conversational-text-to-sql'
    table_question_answering_pipeline = 'table-question-answering-pipeline'
    sentence_embedding = 'sentence-embedding'
    text_ranking = 'text-ranking'
    mgeo_ranking = 'mgeo-ranking'
    relation_extraction = 'relation-extraction'
    document_segmentation = 'document-segmentation'
    extractive_summarization = 'extractive-summarization'
    feature_extraction = 'feature-extraction'
    mglm_text_summarization = 'mglm-text-summarization'
    codegeex_code_translation = 'codegeex-code-translation'
    codegeex_code_generation = 'codegeex-code-generation'
    glm130b_text_generation = 'glm130b-text-generation'
    translation_en_to_de = 'translation_en_to_de'  # keep it underscore
    translation_en_to_ro = 'translation_en_to_ro'  # keep it underscore
    translation_en_to_fr = 'translation_en_to_fr'  # keep it underscore
    token_classification = 'token-classification'
    translation_evaluation = 'translation-evaluation'
    user_satisfaction_estimation = 'user-satisfaction-estimation'
    siamese_uie = 'siamese-uie'
    document_grounded_dialog_retrieval = 'document-grounded-dialog-retrieval'
    document_grounded_dialog_rerank = 'document-grounded-dialog-rerank'
    document_grounded_dialog_generate = 'document-grounded-dialog-generate'
    language_identification = 'language_identification'

    # audio tasks
    sambert_hifigan_tts = 'sambert-hifigan-tts'
    speech_dfsmn_aec_psm_16k = 'speech-dfsmn-aec-psm-16k'
    speech_frcrn_ans_cirm_16k = 'speech_frcrn_ans_cirm_16k'
    speech_dfsmn_ans_psm_48k_causal = 'speech_dfsmn_ans_psm_48k_causal'
    speech_dfsmn_kws_char_farfield = 'speech_dfsmn_kws_char_farfield'
    speech_separation = 'speech-separation'
    kws_kwsbp = 'kws-kwsbp'
    asr_inference = 'asr-inference'
    asr_wenet_inference = 'asr-wenet-inference'
    itn_inference = 'itn-inference'
    punc_inference = 'punc-inference'
    sv_inference = 'sv-inference'
    speaker_diarization_inference = 'speaker-diarization-inference'
    vad_inference = 'vad-inference'
    speaker_verification = 'speaker-verification'
    speaker_verification_rdino = 'speaker-verification-rdino'
    speaker_verification_eres2net = 'speaker-verification-eres2net'
    speaker_change_locating = 'speaker-change-locating'
    lm_inference = 'language-score-prediction'
    speech_timestamp_inference = 'speech-timestamp-inference'

    # multi-modal tasks
    image_captioning = 'image-captioning'
    multi_modal_embedding = 'multi-modal-embedding'
    generative_multi_modal_embedding = 'generative-multi-modal-embedding'
    visual_question_answering = 'visual-question-answering'
    visual_grounding = 'visual-grounding'
    visual_entailment = 'visual-entailment'
    multi_modal_similarity = 'multi-modal-similarity'
    text_to_image_synthesis = 'text-to-image-synthesis'
    video_multi_modal_embedding = 'video-multi-modal-embedding'
    image_text_retrieval = 'image-text-retrieval'
    ofa_ocr_recognition = 'ofa-ocr-recognition'
    ofa_asr = 'ofa-asr'
    ofa_sudoku = 'ofa-sudoku'
    ofa_text2sql = 'ofa-text2sql'
    video_captioning = 'video-captioning'
    video_question_answering = 'video-question-answering'
    diffusers_stable_diffusion = 'diffusers-stable-diffusion'
    disco_guided_diffusion = 'disco_guided_diffusion'
    document_vl_embedding = 'document-vl-embedding'
    chinese_stable_diffusion = 'chinese-stable-diffusion'
    text_to_video_synthesis = 'latent-text-to-video-synthesis'  # latent-text-to-video-synthesis
    gridvlp_multi_modal_classification = 'gridvlp-multi-modal-classification'
    gridvlp_multi_modal_embedding = 'gridvlp-multi-modal-embedding'
    soonet_video_temporal_grounding = 'soonet-video-temporal-grounding'
    efficient_diffusion_tuning = 'efficient-diffusion-tuning'
    multimodal_dialogue = 'multimodal-dialogue'

    # science tasks
    protein_structure = 'unifold-protein-structure'



class CustomDatasets(object):
    """ Names for different dataset.
    """
    PairedDataset = 'PairedDataset'
    SiddDataset = 'SiddDataset'
    GoproDataset = 'GoproDataset'
    RedsDataset = 'RedsDataset'


