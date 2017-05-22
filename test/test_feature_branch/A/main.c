/* added in A */
int str_len(char *string)
{
    char *count = string;
    while(*count) {count++;}
    return count - string;
}

/* added in A*/
char* str_append(char* string, char* append) {
    char* newstring = NULL;
    size_t needed = snprintf(NULL, 0, "%s%s", string, append);
    newstring = malloc(needed);
    sprintf(newstring, "%s%s", string, append);
    return newstring;
}

