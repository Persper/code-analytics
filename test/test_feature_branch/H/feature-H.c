/* added in H */
struct node
{
    int data;
    struct node *next;
}*head;
 
/* added in H */
void append(int num)
{
    struct node *temp,*right;
    temp= (struct node *)malloc(sizeof(struct node));
    temp->data=num;
    right=(struct node *)head;
    while(right->next != NULL)
    right=right->next;
    right->next =temp;
    right=temp;
    right->next=NULL;
}

/* added in H */
void add( int num )
{
    struct node *temp;
    temp=(struct node *)malloc(sizeof(struct node));
    temp->data=num;
    if (head== NULL)
    {
        head=temp;
        head->next=NULL;
    }
    else
    {
        temp->next=head;
        head=temp;
    }
}

/* added in H */ 
void insert(int num)
{
    int c=0;
    struct node *temp;
    temp=head;
    if(temp==NULL)
    {
        add(num);
    }
    else
    {
        while(temp!=NULL)
        {
            if(temp->data<num)
            c++;
            temp=temp->next;
        }
        if(c==0)
            add(num);
        else if(c<count())
            addafter(num,++c);
        else
            append(num);
    }
}