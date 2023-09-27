from datetime import datetime
import heapq
from .helpers.DateAuxiliary import aux_data
from .helpers.Suggestion import Suggestion

REPLACE_W = 1
REMOVE_W = 1.2
ADD_W = 1.2

DAY_RANGE = [1, 31]
MONTH_RANGE = [1, 12]
YEAR_RANGE = [1950, datetime.now().year]


def correct_date_char(char:str, format:str, months_chars:list) -> list:
    '''
    @description:
        This function corrects a given character using a saved dictionary of
        similar characters according to a given format (character type)
    @input:
        char: the character to be corrected
        format: the format types of the incoming characters
                format[0] represents the current character type
                n => number
                s => separator
                a => alphabet
        months_chars: the possible characters that char can be corrected to if
                      the current format is an alphabet
    @output:
        corrected_chars: a list of strings each representing a possible correction
                         for the given character according to the given format
    '''
    corrected_chars = []

    if format[0] == 'n':
        for key in similarChars:
            if char in similarChars[key]:
                if len(key) == 1 or format[:2] == 'ns':
                    corrected_chars.append(key)
    if format[0] == 's':
        for key in similarSeps:
            if char in similarSeps[key]:
                corrected_chars.append(key)
    if format[0] == 'a':
        for key in similarAlpha:
            if char in similarAlpha[key] and key in months_chars:
                corrected_chars.append(key)

    if len(corrected_chars) == 0:
        return [None]
    else:
        return corrected_chars
    

def verify_number(char:str, format:str) -> bool:
    '''
    @description:
        This function checks if the given character is a valid character to be
        positioned in a specific position in the date according to the its
        format type and the format type of the characters following it
    @input:
        char: the character to be verified
        format: the format types of the incoming characters
                n => number
    @output:
        True if the character is valid to be positioned in the date
        False if the character is not valid to be positioned in the date
    '''
    char = int(char)
    if format[:4] == 'nnnn':
        if char == 1 or char == 2:
            return True
    elif format[:3] == 'nnn':
        if char == 0 or char == 9:
            return True
    elif format[:2] == 'nn':
        if char <= 3 and char >= 5:
            return True
    else:
        return True
    return False


def correct_date_num(char:str, format:str) -> list:
    '''
    @description:
        This function corrects a given number character with a series of all
        possible number corrections
    @input:
        char: the number character to be corrected
        format: the format types of the incoming characters
                format[0] represents the current character type
                n => number
    @output:
        corrected_nums: list of strings each representing a possible correction
                        for the given character according to the given format
    '''
    corrected_nums = []

    if format[0] == 'n':
        for key in similarNums:
            if char in similarNums[key] and verify_number(key, format):
                corrected_nums.append(key)
        
    return corrected_nums


def get_min_suggestions(suggestions:list, minimums_cnt:int) -> list:
    '''
    @description:
        This function minimizes the number of suggestions by taking only the suggestions
        that have a levenshtein distance smaller than or equal to the nth smallest
        levenshtein distance where n is determined by minimums_cnt
    @input:
        suggestions: list of objects of class Suggestion representing each suggestion
        minimums_cnt: the number of minimum levenshtein distances that should be taken
                      in consideration when filtering the suggestions
    @output:
        new_suggestions: list of objects of class Suggestion representing the
                         minimized suggestions
    '''
    suggestions = set(suggestions)
    accuracies = set(map(lambda x: x.accuracy, suggestions))
    minimums = heapq.nsmallest(minimums_cnt, accuracies)
    new_suggestions = list(filter(lambda x: x.accuracy <= minimums[-1], suggestions))

    return new_suggestions


def update_months(months:list, char:str) -> list:
    '''
    @description:
        This function filters the list of months by selecting the months that start
        with char and updates the filtered list by removing the first character
        of each month
    @input:
        months: list of strings representing the subsets of months that could be
                a potential correction of the rest of the date month
        char: the character according which the months are to be filtered
    @output:
        new_months: list of strings representing the updated months subsets
    '''
    new_months = []
    for month in months:
        if month[0] == char:
            new_months.append(month[1:])
    return new_months
   

def get_status(date:str, format:str, months:list) -> dict:
    '''
    @description:
        This function gets the current status of the backtracking algorithm by
        determining if the current character needs correction, what the possible
        corrected characters are, and what the possible added characters are
    @input:
        date: the remaining date subset
        format: the format types of each character of the remaining date subset
    @output:
        status: dictionary of information representing the state of the backtracking
                algorithm current state
                status['condition'] => bool variable representing whether the current
                                       character is correct or not
                status['corrected'] => list of strings representing the possible
                                       corrected characters for the current character
                status['added'] => list of strings representing the possible added
                                   characters that should be added before the current
                                   character
    '''
    status = {
        'condition': False,
        'corrected': None,
        'added': None
    }
    months_chars = []

    if format[0] == 'n':
        if format[:4] == 'nnnn':
            status['added'] = list(similarNums)[1:3]
        elif format[:3] == 'nnn':
            status['added'] = list(similarNums)[0]
        else:
            status['added'] = list(similarNums)[1]
        status['condition'] = (date[0] in similarChars)

    elif format[0] == 's':
        status['added'] = list(similarSeps)[-2]
        status['condition'] = (date[0] in similarSeps)

    elif format[0] == 'a':
        months_chars = list(set(map(lambda x: x[0], months)))
        status['added'] = months_chars
        status['condition'] = (date[0] in months_chars)

    if status['condition']:
        status['corrected'] = [date[0]] + correct_date_num(date[0], format)
    else:
        status['corrected'] = correct_date_char(date[0], format, months_chars)

    return status


def form_new_sugg(suggestion:Suggestion, char:str, weight:float) -> Suggestion:
    '''
    @description:
        This function uses given data to edit the values of the given suggestion and
        make a new suggestion of these values
    @input:
        suggestion: object of class Suggestion representing the suggestion to be
                    updated
        char: the character to be added to the proposed suggestion date
        weight: the weight to be added to the proposed suggestion levenshtein distance
    @output:
        Suggestion class object representing the new updated suggestion
    '''
    return Suggestion(
        char + suggestion.date,
        weight + suggestion.accuracy,
    )


def get_combined_results(possibilities:dict, conditions:bool, correct_chars:list, added_chars:list) -> list:
    '''
    @description:
        This function updates the suggestions of the sub-problems of the backtracking
        algorithm by adding the corrected characters to the suggested date, adding
        the weight of the change that took place (replacement, addition, or removal),
        then combines them into one list of updated suggestions
    @input:
        possibilities: dictionary of all possible suggestions coming from the
                       sub-problems of the backtracking algorithm
                       possibilites['replaced'] => a list of lists each containing objects
                                                   of class Suggestion representing the
                                                   suggestions resulted from character
                                                   replacement operations
                       possibilites['added'] => a list of lists each containing objects
                                                   of class Suggestion representing the
                                                   suggestions resulted from character
                                                   addition operations
                       possibilites['removed'] => a list of objects of class Suggestion
                                                  representing the suggestions resulted
                                                  from character removal operations
        correct_chars: a list of the same size as possibilites['replaced'] containing
                       possible character corrections for each sub-list in
                       possibilites['replaced']
        added_chars: a list of the same size as possibilites['added'] containing
                       possible character additions for each sub-list in
                       possibilites['added']
    @output:
        results: list of objects of class Suggestion representing the combined
                 suggestions of all operations (replacements, additions, and removals)
    '''
    results = []

    if conditions == True:
        for sugg in possibilities['replaced'][0]:
            results.append(
                form_new_sugg(sugg, correct_chars[0], 0)
            )
        for i in range(1, len(possibilities['replaced'])):
            for sugg in possibilities['replaced'][i]:
                results.append(
                    form_new_sugg(sugg, correct_chars[i], REPLACE_W)
                )
    else:
        for i in range(len(possibilities['replaced'])):
            if correct_chars[i] != None:
                for sugg in possibilities['replaced'][i]:
                    results.append(
                        form_new_sugg(sugg, correct_chars[i], REPLACE_W)
                    )
    
    for i in range(len(possibilities['added'])):
        for sugg in possibilities['added'][i]:
            results.append(
                form_new_sugg(sugg, added_chars[i], ADD_W)
            )

    for sugg in possibilities['removed']:
        results.append(
            form_new_sugg(sugg, '', REMOVE_W)
        )

    return results


def get_possibilities(date:str, format:str, months:list, dp:dict=dict()) -> list:
    '''
    @description:
        This function is the base of the date correction algorithm which uses a
        backtracking algorithm with dynamic programming to try all possible
        combinations of character replacements, additions, and removals to
        get suggestions for the date correction
    @input:
        date: the actual date given for correction or a subset of the actual given date
        format: string of character formats that the date should be compared to
        months: list of possible months or subsets of months that the date could contain
        dp: a dynamic programming dictionary for storing the parameters of the
            backtracking algorithm along with the return values (suggestions) of
            these parameters
    @output:
        suggestions: the list of objects of class Suggestion representing the list
                     of all possible date correction suggestions
    '''
    # stopping condition
    if len(date) == 0:
        if len(format) == 0:
            return [Suggestion('', 0)]
        elif len(format) == 1:
            return [Suggestion(list(similarNums)[1], ADD_W*len(format))]
        return []
    if len(format) == 0:
        return [Suggestion('', REMOVE_W*len(date))]
    
    # dynamic programming restoring
    if date in dp:
        if format in dp[date]:
            if str(months) in dp[date][format]:
                return dp[date][format][str(months)]
    
    # get necessary information for recursive call
    status = get_status(date, format, months)
    conditions = status['condition']
    corrected_chars = status['corrected']
    added_chars = status['added']

    # initialize possibilities dictionary
    possibilities = {
        'replaced': [],
        'added': [],
        'removed': None
    }

    # recursive call for replacement
    for i in range(len(corrected_chars)):
        date_jump = 1
        format_jump = 1
        if corrected_chars[i] != None:
            date_jump = len(corrected_chars[i])
            format_jump = date_jump      

        if format[0] == 'a':
            months_corrected = update_months(months, corrected_chars[i])
            if len(months_corrected) == 1 and months_corrected[0] == '':
                format_jump = format.index('s')
        else:
            months_corrected = months

        possibilities['replaced'].append(
            get_possibilities(date[date_jump:], format[format_jump:], months_corrected, dp)
        )

    # recursive call for adding
    for i in range(len(added_chars)):
        format_jump = 1
        if format[0] == 'a':
            months_added = update_months(months, added_chars[i])
            if len(months_added) == 1 and months_added[0] == '':
                format_jump = format.index('s')
        else:
            months_added = months

        possibilities['added'].append(
            get_possibilities(date, format[format_jump:], months_added, dp)
        )

    # recursive call for removal
    possibilities['removed'] = get_possibilities(date[1:], format, months, dp)

    # combining and minimizing suggestions
    suggestions = get_combined_results(possibilities,
                                       conditions, corrected_chars, added_chars)
    suggestions = get_min_suggestions(suggestions, 2)

    # dynamic programming storing
    if date in dp:
        if format in dp[date]:
            dp[date][format][str(months)] = suggestions
        else:
            dp[date][format] = {str(months): suggestions}
    else:
        dp[date] = {format: {str(months): suggestions}}
    return suggestions


def fix_separations(suggestions:list) -> list:
    '''
    @description:
        This function checks if there is an inconsistency between the separators of
        the date (forward slash, dash, dot, or space), and if there is, it corrects
        one of them into the other
    @input:
        suggestions: list of objects of class Suggestion representing the list of
                     possible suggestions for date correction
    @output:
        filtered: the list of objects of class Suggestion representing the new list
                  of date correction suggestions with corrected separators
    '''
    filtered = []

    for sugg in suggestions:
        firstSep = ''
        secondSep = ''
        for char in sugg.date:
            if char in similarSeps:
                if firstSep == '':
                    firstSep = char
                else:
                    secondSep = char
                    break
        if firstSep != secondSep:
            if list(similarSeps).index(firstSep) < list(similarSeps).index(secondSep):
                new_sugg = sugg.date.replace(secondSep, firstSep)
            else:
                new_sugg = sugg.date.replace(firstSep, secondSep)
            edits = REPLACE_W + sugg.accuracy
            filtered.append(
                Suggestion(new_sugg, edits)
            )
        else:
            filtered.append(sugg)

    return filtered


def edits_to_accuracy(suggestions:list, date:str) -> list:
    '''
    @description:
        This function converts the levenshtein distances of the suggestions into
        accuracies
    @input:
        suggestions: list of objects of class Suggestion representing the list of
                     possible suggestions for date correction
    @output:
        new_suggestions: the list of objects of class Suggestion representing the
                         new list of date correction suggestions with accuracies
                         instead of levenshtein distances
    '''
    new_suggestions = []

    for sugg in suggestions:
        edits_cnt = sugg.accuracy
        cer_value = edits_cnt/len(date)
        accuracy = round((1-cer_value) * 100, 2)
        if accuracy > 0:
            new_suggestions.append(
                Suggestion(sugg.date, accuracy)
            )

    return new_suggestions


def get_separation_type(date:str) -> str:
    '''
    @description:
        This function iterates over the date to find out the type of used separator
        (forward slash, dash, dot, or space)
    @input:
        date: a string representing a date
    @output:
        a character representing the separator used in the date
    '''
    for char in date:
        if not char.isdigit():
            return char


def get_possible_section_types(section:str) -> list:
    '''
    @description:
        This function gets all possible date section types whether it might be a
        day, month, or year
    @input:
        section: a string representing a section of the three sections of a date 
    @output:
        types: a list of strings, each representing whether this section can
               be a day, month, or year
               d => day
               m => month
               y => year
    '''
    types = []
    if len(section) == 3:
        if section in map(lambda x: x[:3], months):
            types.append('m')
    elif section in months:
        types.append('m')
    else:
        section_int = int(section)
        if len(section) == 4:
            if section_int in range(YEAR_RANGE[0], YEAR_RANGE[1]+1):
                types.append('y')
        elif section_int in range(DAY_RANGE[0], DAY_RANGE[1]+1):
            types.append('d')
            if section_int <= YEAR_RANGE[1] % 100:
                types.append('y')
                if section_int <= 12:
                    types.append('m')
        elif YEAR_RANGE[0] < 2000 and section_int >= YEAR_RANGE[0] % 100:
            types.append('y')
    
    return types


def estimate_date_order(date:str) -> list:
    '''
    @description:
        This function estimates the order of the day, month, and year sections
        of the date (estimates the format of the date)
    @input:
        date: a string representing a date
    @output:
        new_orders: a list of possible orders (formats) that the date can be in
    '''
    sep = get_separation_type(date)
    splitted = date.split(sep)

    new_orders = possibleOrders

    for i in range(len(splitted)):
        types = get_possible_section_types(splitted[i])

        if len(types) == 0:
            return []

        new_orders = list(filter(lambda x: x[i] in types, new_orders))

    return new_orders


def filter_suggestions(suggestions:list) -> list:
    '''
    @description:
        This function filters the date correction suggestions by removing the
        suggestions that might not conform with the rules of dates or that
        have no possible formats
    @input:
        suggestions: list of objects of class Suggestion representing the list of
                     possible suggestions for date correction
    @output:
        new_suggestions: the list of objects of class Suggestion representing the filtered
                     list of date correction suggestions that have possible formats
    '''
    new_suggestions = []
    for sugg in suggestions:
        estimations = estimate_date_order(sugg.date)
        
        if len(estimations) != 0:
            new_suggestions.append(sugg)

    return new_suggestions


def round_suggestion_edits(suggestions:list) -> list:
    '''
    @description:
        This function rounds the suggestions accuracies to 4 decimal places
    @input:
        suggestions: list of objects of class Suggestion representing the list of
                     possible suggestions for date correction
    @output:
        new_suggestions: the list of objects of class Suggestion representing the
                         new list of date correction suggestions with rounded
                         accuracies
    '''
    new_suggestions = []
    for sugg in suggestions:
        new_suggestions.append(
            Suggestion(sugg.date, round(sugg.accuracy,4))
        )

    return new_suggestions


def correctDate(date:str, language:str) -> list:
    '''
    @description:
        This function is the main function that gets a date and a language as input
        and corrects the date according to the auxiliary data of this language
    @input:
        date: a string representing a date to be corrected
        language: a string representing the first two characters of the language
                  of the date ('en', 'ar', ...)
    @output:
        new_suggestions: list of tuples representing the list of possible suggestions
                         for date correction
    '''
    global aux_data

    if not isinstance(date, str):
        raise TypeError('date must be a string!!')
    if not isinstance(language, str):
        raise TypeError('language must be a string!!')
    if language not in aux_data:
        raise ValueError('invalid language value!!')

    date = date.strip()
    if date == '':
        return date
    
    data = aux_data[language]

    global similarChars
    global similarAlpha
    global similarSeps
    global similarNums
    global months
    global possibleOrders

    similarChars = data['similarChars']
    similarAlpha = data['similarAlpha']
    similarSeps = data['similarSeps']
    similarNums = data['similarNums']
    dateFormats = data['dateFormats']
    months = data['months']
    possibleOrders = data['possibleOrders']
    
    suggestions = []
    dp = dict()
    for format in dateFormats:
        suggestions.extend(get_possibilities(date, format, months, dp))
    
    suggestions = get_min_suggestions(suggestions, 2)
    suggestions = fix_separations(suggestions)
    suggestions = filter_suggestions(suggestions)
    suggestions = round_suggestion_edits(suggestions)
    suggestions = get_min_suggestions(suggestions, 1)

    suggestions = edits_to_accuracy(suggestions, date)
    suggestions.sort(key=lambda x: (x.accuracy, len(x.date)), reverse=True)

    new_suggestions = []
    for sugg in suggestions:
        new_suggestions.append(sugg.listify())

    return new_suggestions


def listLanguages() -> list:
    '''
    @description:
        This function returns all the available languages that can be used for
        date correction
    @input:
        none
    @output:
        list of 2-character strings representing the initials of the available
        languages
    '''
    return list(aux_data)