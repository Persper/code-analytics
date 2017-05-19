/* added in G */
char* str_replace(char* search, char* replace, char* subject) {
    char* newstring = "";
    int i = 0;
    for(i = 0; i < str_len(subject); i++) {
        if (subject[i] == search[0]) {
            int e = 0;
            char* calc = "";
            for(e = 0; e < str_len(search); e++) {
                if(subject[i+e] == search[e]) {
                    calc = str_append_chr(calc, search[e]);
                }
            }
            if (str_equals(search, calc) == 0) {
                newstring = str_append(newstring, replace);
                i = i + str_len (search)-1;
            }
            else {
                newstring = str_append_chr(newstring, subject[i]);
            }
        }
        else {
            newstring = str_append_chr(newstring, subject[i]);
        }
    }
    return newstring;
}