class BaseSelectors:
    GONEXT_BUTTON: str = None


class CommonSelectors(BaseSelectors):
    OPTION = 'option[value = "{}"]'
    SELECT = 'select[id = "{}"]'
    INPUT = 'input[{key} = "{value}"]'
    LOADER = '//div[contains(@class, "loader-card")]'


class LoginPageSelectors(BaseSelectors):
    LANGUAGE = '[onclick="selectLanguageRu(window.location); return false;"]'
    SELECT_EDS = '[onclick="showLoader(); selectSignType(); return false;"]'

    IIN_FIELD_LOGIN = '//input[contains(@placeholder, "ИИН/БИН")]'
    PASSWORD_FIELD_LOGIN = '//input[contains(@placeholder, "Пароль")]'
    LOGIN_BUTTON = '//input[contains(@value, "Войти")]'


class SelectOptionSelectors(BaseSelectors):
    CASE_TYPE_SELECT = '//select[contains(@id, "case-type")]'
    INSTANCE_SELECT = '//select[contains(@id, "instance")]'
    DOC_TYPE_SELECT = '//select[contains(@id, "request")]'

    GONEXT_BUTTON = '//input[contains(@value, "Отправить")]'


class FillInfoPageSelectors(BaseSelectors):
    CATEGORY_GROUP_SELECT = '//select[contains(@id, "edit-categoryGroup")]'
    CATEGORY_SELECT = '//select[contains(@id, "edit-category")]'
    CHARACTER_SELECT = '//select[contains(@id, "edit-character")]'
    CITY_SELECT = '//select[contains(@id, "edit-district")]'
    COURT_SELECT = '//select[contains(@id, "edit-court")]'

    ADD_PARTICIPANT_BUTTON = '[onclick="renderAddPersonModalDialog()"]'
    PARTICIPANT_TYPE_SELECT = '//select[contains(@id, "pp-type")]'
    PARTICIPANT_SIDE_SELECT = '//select[contains(@id, "pp-side")]'
    PARTICIPANT_GOTO_BUTTON = '//input[contains(@value, "Далее")]'

    ORG_SEARCH_BUTTON = '//span[contains(@onclick,"fillOrgData")]'

    ORG_BIN = '//input[contains(@id,"org-bin")]'
    ORG_NAME = '//input[contains(@id,"org-name")]'
    ORG_JUR_ADDRESS = '//input[contains(@id,"org-jurAddress")]'
    ORG_FACT_ADDRESS = '//input[contains(@id,"org-factAddress")]'
    ORG_BANK_DETAILS = '//input[contains(@id,"org-bankDetails")]'

    PERSON_SEARCH_BUTTON = '//span[contains(@onclick,"fillPersonData")]'

    PERSON_IIN = '//input[contains(@id,"person-iin")]'
    PERSON_PHONE = '//input[contains(@id,"person-phone")]'
    PERSON_THIRD_NAME = '//input[contains(@id,"person-patronymic")]'
    PERSON_LIVE_PLACE = '//input[contains(@id,"person-livePlace")]'

    FIZ_SAVE_BUTTON = '//input[contains(@onclick,"fillFizHideFields")]'
    JUR_SAVE_BUTTON = '//input[contains(@onclick, "incId") and contains(@class, "btn btn-primary") and contains(@value, "Сохранить")]'

    MODAL_DIALOG_PANEL = '//div[contains(@id, "questModalDialogPanel")]'
    QUEST_BLOCK_CONTAINER_CLASS = "quest-block-container"
    NEXT_QUEST_BUTTONS = '//input[@value="Далее" and @type="submit"]'
    TRIGGER_CONSTRUCTOR_BUTTON = (
        '//a[contains(@onclick, "showQuestionModalDialogLoan()")]'
    )
    DIALOG_VALUE = '//input[@value="{dialog_value}"]'

    GONEXT_BUTTON = '//a[contains(@onclick, "goNext()")]'


class PaymentPageSelectors(BaseSelectors):
    KBK_SELECT = '//select[contains(@id, "selectKbk")]'

    DEBT_SUM_FIELD = '//input[contains(@id, "edit-totalSum")]'
    STATE_DUTY_SUM_FIELD = '//input[contains(@id, "edit-duty")]'

    FILE_UPLOAD_INPUT = 'input[type="file"]'
    FILE_UPLOAD_BUTTON = 'input[value = "Прикрепить файл"]'

    ONLINE_PAY_BUTTON = '//a[contains(@onclick, "doPay1")]'
    CHECK_PAYMENT_BUTTON = '//a[contains(@onclick, "doCheckPayments")]'
    PAYMENT_CODE_ID = "ctl00_CPH1_payCodeValue"

    IS_ONLINE_PAY_CHECKBOX = '//input[contains(@id, "isonline-payment")]'

    GONEXT_BUTTON = '//a[contains(@onclick, "goToDocuments()")]'


class UploadFilesPageSelectors(BaseSelectors):
    BASE_REQ_FIELD = '//textarea[contains(@id, "edit-plaint-description")]'
    ADDITIONAL_REQ_FIELD = '//textarea[contains(@id, "edit-plaint-additional")]'

    STATEMENT_UPLOAD_INPUT = 'input[type="file"]:not([multiple])'
    FILE_UPLOAD_INPUT = 'input[multiple="multiple"]'

    CONTRACT_DATE_INPUT = '//input[contains(@id, "contract-date-field")]'
    TERM_DATE_INPUT = '//input[contains(@id, "term-date-field")]'
    LOAN_SUM_INPUT = '//input[contains(@id, "sum-field")]'
    TERMINATION_INFO_INPUT = '//input[contains(@id, "termination-field")]'
    VIOLATION_INFO_INPUT = '//textarea[contains(@id, "essenceVolation-field")]'
    PRETRIAL_RESULTS_INPUT = '//textarea[contains(@id, "measures-field")]'

    STATEMENT_REQ_BUTTON = '//input[contains(@value, "Добавить") and @class="button button-primary" and @type="submit"]'
    STATEMENT_REQ_TEXTFIELD = (
        '//input[contains(@type, "text") and @style="flex: 1" and not(@value)]'
    )

    FILE_TYPE_REJECT = 'span[id="fileTypeRejectAlertMsg"]'

    GONEXT_BUTTON = '//a[contains(@onclick, "goToSign()")]'


class SigningPageSelectors(BaseSelectors):
    SIGN_BUTTON = (
        '//input[contains(@onclick, "showLoader(); selectSignType(); return false;")]'
    )
    DOWNLOAD_RESULT_FILE_BUTTON = 'input[value = "Скачать талон об отправке"]'
