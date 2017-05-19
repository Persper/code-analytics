/* added in J, edited in K */
void display(struct node *r)
{
    r=head;
    if(r==NULL)
    {
        return;
    }
    printf("\n");
}
 
/* added in J */ 
int count()
{
    struct node *n;
    int c=0;
    n=head;
    while(n!=NULL)
    {
        n=n->next;
        c++;
    }
    return c;
}