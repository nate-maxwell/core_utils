import pytest

from core import regex


class TestGetFileVersionNumber:
    def test_get_file_version_number_standard_format(self) -> None:
        result = regex.get_file_version_number("GhostA_anim_v001.ma")
        assert result == "001"

    def test_get_file_version_number_different_padding(self) -> None:
        result = regex.get_file_version_number("file_v12.txt")
        assert result == "12"

    def test_get_file_version_number_large_padding(self) -> None:
        result = regex.get_file_version_number("asset_v00123.fbx")
        assert result == "00123"

    def test_get_file_version_number_single_digit(self) -> None:
        result = regex.get_file_version_number("model_v1.obj")
        assert result == "1"

    def test_get_file_version_number_different_extension(self) -> None:
        result = regex.get_file_version_number("texture_v005.png")
        assert result == "005"

    def test_get_file_version_number_multiple_dots(self) -> None:
        result = regex.get_file_version_number("file.backup_v003.tar.gz")
        assert result == "003"

    def test_get_file_version_number_no_version(self) -> None:
        result = regex.get_file_version_number("simple_file.txt")
        assert result is None

    def test_get_file_version_number_wrong_format(self) -> None:
        result = regex.get_file_version_number("file_version1.txt")
        assert result is None

    def test_get_file_version_number_v_not_before_extension(self) -> None:
        result = regex.get_file_version_number("file_v001_backup.txt")
        assert result is None

    def test_get_file_version_number_no_extension(self) -> None:
        result = regex.get_file_version_number("file_v001")
        assert result is None

    def test_get_file_version_number_empty_string(self) -> None:
        result = regex.get_file_version_number("")
        assert result is None

    def test_get_file_version_number_with_path(self) -> None:
        result = regex.get_file_version_number("C:/folder/asset_v042.ma")
        assert result == "042"


class TestIsPathLike:
    # Windows absolute paths
    def test_is_path_like_windows_drive_backslash(self) -> None:
        assert regex.is_path_like("C:\\Users\\Documents") is True

    def test_is_path_like_windows_drive_forward_slash(self) -> None:
        assert regex.is_path_like("C:/Users/Documents") is True

    def test_is_path_like_different_drive_letter(self) -> None:
        assert regex.is_path_like("D:\\Projects\\file.txt") is True

    def test_is_path_like_lowercase_drive(self) -> None:
        assert regex.is_path_like("c:\\temp") is True

    # UNC paths
    def test_is_path_like_unc_path(self) -> None:
        assert regex.is_path_like("\\\\server\\share\\folder") is True

    def test_is_path_like_unc_path_short(self) -> None:
        assert regex.is_path_like("\\\\server\\share") is True

    # Relative paths
    def test_is_path_like_current_directory(self) -> None:
        assert regex.is_path_like(".\\file.txt") is True

    def test_is_path_like_parent_directory(self) -> None:
        assert regex.is_path_like("..\\folder\\file.txt") is True

    # Paths with slashes
    def test_is_path_like_contains_backslash(self) -> None:
        assert regex.is_path_like("folder\\subfolder") is True

    def test_is_path_like_contains_forward_slash(self) -> None:
        assert regex.is_path_like("folder/subfolder") is True

    # Filenames with extensions
    def test_is_path_like_simple_filename(self) -> None:
        assert regex.is_path_like("document.txt") is True

    def test_is_path_like_common_extensions(self) -> None:
        assert regex.is_path_like("file.pdf") is True
        assert regex.is_path_like("image.png") is True
        assert regex.is_path_like("archive.zip") is True

    def test_is_path_like_long_extension(self) -> None:
        assert regex.is_path_like("file.backup") is True

    def test_is_path_like_extension_max_length(self) -> None:
        assert regex.is_path_like("file.abcdef") is True

    # Not path-like
    def test_is_path_like_plain_text(self) -> None:
        assert regex.is_path_like("hello world") is False

    def test_is_path_like_no_extension_no_slashes(self) -> None:
        assert regex.is_path_like("filename") is False

    def test_is_path_like_single_char_extension(self) -> None:
        assert regex.is_path_like("file.c") is True

    def test_is_path_like_too_long_extension(self) -> None:
        assert regex.is_path_like("file.toolong") is False

    def test_is_path_like_empty_string(self) -> None:
        assert regex.is_path_like("") is False

    def test_is_path_like_non_string_input(self) -> None:
        assert regex.is_path_like(123) is False
        assert regex.is_path_like(None) is False
        assert regex.is_path_like([]) is False

    def test_is_path_like_url(self) -> None:
        # URLs contain slashes but are path-like in this context
        assert regex.is_path_like("http://example.com/page") is True

    def test_is_path_like_dot_only(self) -> None:
        assert regex.is_path_like(".") is False

    def test_is_path_like_extension_only(self) -> None:
        assert regex.is_path_like(".txt") is False


class TestPascaleToSnake:
    def test_pascal_to_snake_simple(self) -> None:
        assert regex.pascal_to_snake("PascalCase") == "pascal_case"

    def test_pascal_to_snake_single_word(self) -> None:
        assert regex.pascal_to_snake("Word") == "word"

    def test_pascal_to_snake_multiple_words(self) -> None:
        assert regex.pascal_to_snake("ThisIsATest") == "this_is_a_test"

    def test_pascal_to_snake_with_numbers(self) -> None:
        assert regex.pascal_to_snake("Version2Update") == "version2_update"

    def test_pascal_to_snake_consecutive_capitals(self) -> None:
        assert regex.pascal_to_snake("HTTPServer") == "http_server"

    def test_pascal_to_snake_ending_with_capital(self) -> None:
        assert regex.pascal_to_snake("GetHTTP") == "get_http"

    def test_pascal_to_snake_acronym(self) -> None:
        assert regex.pascal_to_snake("XMLParser") == "xml_parser"

    def test_pascal_to_snake_already_lowercase(self) -> None:
        assert regex.pascal_to_snake("lowercase") == "lowercase"

    def test_pascal_to_snake_empty_string(self) -> None:
        assert regex.pascal_to_snake("") == ""

    def test_pascal_to_snake_single_letter(self) -> None:
        assert regex.pascal_to_snake("A") == "a"

    def test_pascal_to_snake_with_underscores(self) -> None:
        # If input already has underscores, they're preserved
        assert regex.pascal_to_snake("Pascal_Case") == "pascal__case"

    def test_pascal_to_snake_numbers_at_end(self) -> None:
        assert regex.pascal_to_snake("Test123") == "test123"

    def test_pascal_to_snake_numbers_in_middle(self) -> None:
        assert regex.pascal_to_snake("Test123Name") == "test123_name"

    def test_pascal_to_snake_mixed_case(self) -> None:
        assert regex.pascal_to_snake("iPhone") == "i_phone"

    def test_pascal_to_snake_camel_case(self) -> None:
        # Also works for camelCase (starting with lowercase)
        assert regex.pascal_to_snake("camelCase") == "camel_case"

    def test_pascal_to_snake_complex_example(self) -> None:
        assert regex.pascal_to_snake("GetHTTPResponseCode") == "get_http_response_code"

    def test_pascal_to_snake_single_capital_at_end(self) -> None:
        assert regex.pascal_to_snake("testA") == "test_a"


class TestCamelToSnake:

    def test_simple_camel_case(self):
        assert regex.camel_to_snake("myVariable") == "my_variable"
        assert regex.camel_to_snake("userName") == "user_name"
        assert regex.camel_to_snake("firstName") == "first_name"

    def test_multiple_words(self):
        assert regex.camel_to_snake("myLongVariableName") == "my_long_variable_name"
        assert regex.camel_to_snake("thisIsATest") == "this_is_a_test"

    def test_consecutive_capitals(self):
        assert regex.camel_to_snake("HTTPResponse") == "http_response"
        assert regex.camel_to_snake("parseHTMLDocument") == "parse_html_document"
        assert regex.camel_to_snake("XMLParser") == "xml_parser"

    def test_numbers_in_name(self):
        assert regex.camel_to_snake("myVar2Name") == "my_var2_name"
        assert regex.camel_to_snake("test123Value") == "test123_value"
        assert regex.camel_to_snake("var1") == "var1"

    def test_single_word(self):
        assert regex.camel_to_snake("variable") == "variable"
        assert regex.camel_to_snake("test") == "test"

    def test_already_snake_case(self):
        assert regex.camel_to_snake("my_variable") == "my_variable"
        assert regex.camel_to_snake("user_name") == "user_name"

    def test_empty_string(self):
        assert regex.camel_to_snake("") == ""

    def test_single_character(self):
        assert regex.camel_to_snake("a") == "a"
        assert regex.camel_to_snake("A") == "a"

    def test_pascal_case(self):
        assert regex.camel_to_snake("MyVariable") == "my_variable"
        assert regex.camel_to_snake("UserName") == "user_name"

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("camelCase", "camel_case"),
            ("PascalCase", "pascal_case"),
            ("simpleTest", "simple_test"),
            ("aB", "a_b"),
            ("getHTTPResponseCode", "get_http_response_code"),
            ("HTTPResponseCodeXML", "http_response_code_xml"),
        ],
    )
    def test_parametrized_cases(self, input_str, expected):
        assert regex.camel_to_snake(input_str) == expected


class TestPascalToCamel:
    def test_pascal_to_camel_simple(self) -> None:
        assert regex.pascal_to_camel("PascalCase") == "pascalCase"

    def test_pascal_to_camel_single_word(self) -> None:
        assert regex.pascal_to_camel("Word") == "word"

    def test_pascal_to_camel_multiple_words(self) -> None:
        assert regex.pascal_to_camel("ThisIsATest") == "thisIsATest"

    def test_pascal_to_camel_with_numbers(self) -> None:
        assert regex.pascal_to_camel("Version2Update") == "version2Update"

    def test_pascal_to_camel_acronym(self) -> None:
        assert regex.pascal_to_camel("HTTPServer") == "hTTPServer"

    def test_pascal_to_camel_already_camel_case(self) -> None:
        assert regex.pascal_to_camel("alreadyCamel") == "alreadyCamel"

    def test_pascal_to_camel_empty_string(self) -> None:
        assert regex.pascal_to_camel("") == ""

    def test_pascal_to_camel_single_letter(self) -> None:
        assert regex.pascal_to_camel("A") == "a"

    def test_pascal_to_camel_lowercase_word(self) -> None:
        assert regex.pascal_to_camel("lowercase") == "lowercase"

    def test_pascal_to_camel_mixed_case(self) -> None:
        assert regex.pascal_to_camel("MyClassName") == "myClassName"


class TestCamelToPascal:
    def test_camel_to_pascal_simple(self) -> None:
        assert regex.camel_to_pascal("camelCase") == "CamelCase"

    def test_camel_to_pascal_single_word(self) -> None:
        assert regex.camel_to_pascal("word") == "Word"

    def test_camel_to_pascal_multiple_words(self) -> None:
        assert regex.camel_to_pascal("thisIsATest") == "ThisIsATest"

    def test_camel_to_pascal_with_numbers(self) -> None:
        assert regex.camel_to_pascal("version2Update") == "Version2Update"

    def test_camel_to_pascal_acronym(self) -> None:
        assert regex.camel_to_pascal("hTTPServer") == "HTTPServer"

    def test_camel_to_pascal_already_pascal_case(self) -> None:
        assert regex.camel_to_pascal("AlreadyPascal") == "AlreadyPascal"

    def test_camel_to_pascal_empty_string(self) -> None:
        assert regex.camel_to_pascal("") == ""

    def test_camel_to_pascal_single_letter(self) -> None:
        assert regex.camel_to_pascal("a") == "A"

    def test_camel_to_pascal_uppercase_word(self) -> None:
        assert regex.camel_to_pascal("UPPERCASE") == "UPPERCASE"

    def test_camel_to_pascal_mixed_case(self) -> None:
        assert regex.camel_to_pascal("myVariableName") == "MyVariableName"


class TestSnakeToPascal:
    def test_snake_to_pascal_simple(self) -> None:
        assert regex.snake_to_pascal("snake_case") == "SnakeCase"

    def test_snake_to_pascal_single_word(self) -> None:
        assert regex.snake_to_pascal("word") == "Word"

    def test_snake_to_pascal_multiple_words(self) -> None:
        assert regex.snake_to_pascal("this_is_a_test") == "ThisIsATest"

    def test_snake_to_pascal_with_numbers(self) -> None:
        assert regex.snake_to_pascal("version_2_update") == "Version2Update"

    def test_snake_to_pascal_numbers_in_word(self) -> None:
        assert regex.snake_to_pascal("var123_name") == "Var123Name"

    def test_snake_to_pascal_already_pascal_case(self) -> None:
        assert regex.snake_to_pascal("PascalCase") == "Pascalcase"

    def test_snake_to_pascal_empty_string(self) -> None:
        assert regex.snake_to_pascal("") == ""

    def test_snake_to_pascal_single_letter(self) -> None:
        assert regex.snake_to_pascal("a") == "A"

    def test_snake_to_pascal_consecutive_underscores(self) -> None:
        assert regex.snake_to_pascal("my__variable") == "MyVariable"

    def test_snake_to_pascal_leading_underscore(self) -> None:
        assert regex.snake_to_pascal("_my_variable") == "MyVariable"

    def test_snake_to_pascal_trailing_underscore(self) -> None:
        assert regex.snake_to_pascal("my_variable_") == "MyVariable"

    def test_snake_to_pascal_uppercase_words(self) -> None:
        assert regex.snake_to_pascal("HTTP_SERVER") == "HttpServer"

    def test_snake_to_pascal_mixed_case_words(self) -> None:
        assert regex.snake_to_pascal("My_Variable_Name") == "MyVariableName"

    def test_snake_to_pascal_long_name(self) -> None:
        assert regex.snake_to_pascal("get_http_response_code") == "GetHttpResponseCode"

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("my_function_name", "MyFunctionName"),
            ("user_id", "UserId"),
            ("http_response", "HttpResponse"),
            ("a_b_c", "ABC"),
            ("test_123", "Test123"),
        ],
    )
    def test_parametrized_cases(self, input_str, expected):
        assert regex.snake_to_pascal(input_str) == expected


class TestSnakeToCamel:
    def test_snake_to_camel_simple(self) -> None:
        assert regex.snake_to_camel("snake_case") == "snakeCase"

    def test_snake_to_camel_single_word(self) -> None:
        assert regex.snake_to_camel("word") == "word"

    def test_snake_to_camel_multiple_words(self) -> None:
        assert regex.snake_to_camel("this_is_a_test") == "thisIsATest"

    def test_snake_to_camel_with_numbers(self) -> None:
        assert regex.snake_to_camel("version_2_update") == "version2Update"

    def test_snake_to_camel_numbers_in_word(self) -> None:
        assert regex.snake_to_camel("var123_name") == "var123Name"

    def test_snake_to_camel_already_camel_case(self) -> None:
        assert regex.snake_to_camel("camelCase") == "camelcase"

    def test_snake_to_camel_empty_string(self) -> None:
        assert regex.snake_to_camel("") == ""

    def test_snake_to_camel_single_letter(self) -> None:
        assert regex.snake_to_camel("a") == "a"

    def test_snake_to_camel_consecutive_underscores(self) -> None:
        assert regex.snake_to_camel("my__variable") == "myVariable"

    def test_snake_to_camel_leading_underscore(self) -> None:
        assert regex.snake_to_camel("_my_variable") == "myVariable"

    def test_snake_to_camel_trailing_underscore(self) -> None:
        assert regex.snake_to_camel("my_variable_") == "myVariable"

    def test_snake_to_camel_uppercase_words(self) -> None:
        assert regex.snake_to_camel("HTTP_SERVER") == "httpServer"

    def test_snake_to_camel_mixed_case_words(self) -> None:
        assert regex.snake_to_camel("My_Variable_Name") == "myVariableName"

    def test_snake_to_camel_long_name(self) -> None:
        assert regex.snake_to_camel("get_http_response_code") == "getHttpResponseCode"

    def test_snake_to_camel_two_words(self) -> None:
        assert regex.snake_to_camel("user_name") == "userName"

    def test_snake_to_camel_first_word_uppercase(self) -> None:
        assert regex.snake_to_camel("User_name") == "userName"

    @pytest.mark.parametrize(
        "input_str,expected",
        [
            ("my_variable_name", "myVariableName"),
            ("user_id", "userId"),
            ("http_response", "httpResponse"),
            ("a_b_c", "aBC"),
            ("test_123", "test123"),
            ("my_function", "myFunction"),
        ],
    )
    def test_parametrized_cases(self, input_str, expected):
        assert regex.snake_to_camel(input_str) == expected
