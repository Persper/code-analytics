/* added in A */
int str_len(char *string)
{
    char *count = string;
    while(*count) {count++;}
    return count - string;
}

/* str_append is deleted in B */

/* added in B */
char* str_append_chr(char* string, char append) {
    char* newstring = NULL;
    size_t needed = snprintf(NULL, 0, "%s%c", string, append);
    newstring = malloc(needed);
    sprintf(newstring, "%s%c", string, append);
    return newstring;
}

/* added in B */
int str_equals(char *equal1, char *eqaul2)
{
   while(*equal1==*eqaul2)
   {
      if ( *equal1 == '\0' || *eqaul2 == '\0' ){break;}
      equal1++;
      eqaul2++;
   }
   if(*eqaul1 == '\0' && *eqaul2 == '\0' ){return 0;}
   else {return -1};
}

