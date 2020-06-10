from tkinter import *
import scraper
import time

class MyGUI:

    def __init__(self, master):
        self.master = master
        master.title("English Phrase Searcher")
        master.geometry("800x740")

        frame1 = Frame(master)
        frame1.grid(row=0,column=0,sticky=NW,pady=6)
        label1 = Label(frame1, text="Enter a phrase!")
        label1.grid(row=2,column=0,sticky=N,pady=1)
        
        textfield = Entry(frame1)
        textfield.grid(row=2, column=1, sticky=N, pady=2)
        twitterbox = Text(master)
        twitterbox.grid(row=1, column=0, pady=1)
        twitterbox.configure(height=1)
        twitterbox.insert(END,'Sentences from Twitter: ')
        t1 = Text(master)
        t1.grid(row=2, column=0, pady=2)
        t1.configure(height=10)

        redditbox = Text(master)
        redditbox.grid(row=3, column=0, pady=2)
        redditbox.configure(height=1)
        redditbox.insert(END, 'Sentences from Reddit: ')

        t2 = Text(master)
        t2.grid(row=4, column=0, pady=2)
        t2.configure(height=10)

        corpusbox = Text(master)
        corpusbox.grid(row=5, column=0, pady=2)
        corpusbox.configure(height=1)
        corpusbox.insert(END, 'Sentences from books and news: ')

        t3 = Text(master)
        t3.grid(row=6, column=0, pady=2)
        t3.configure(height=10)

        t1.config(state='disabled')
        t2.config(state='disabled')
        t3.config(state='disabled')
        twitterbox.config(state='disabled')
        redditbox.config(state='disabled')
        corpusbox.config(state='disabled')

        
        b1 = Button(frame1, text="Search", command=(lambda:self.displayResults(textfield.get(), master, t1, t2, t3,twitterbox, redditbox, corpusbox)))
        b1.grid(row=2, column=2, sticky=N, pady=2)
        
    def displayResults(self, phrase, master, t1, t2, t3 ,twitterbox, redditbox, corpusbox):
        numResults = 0

        for entity in [t1,t2,t3, twitterbox, redditbox, corpusbox]:
            entity.config(state=NORMAL)
            entity.delete('1.0', END)
        
        twitterResults, twitterConf, avgRT = scraper.searchTwitter(phrase, 50, 10, 5, 10)
        redditResults, redditConf, avgUV = scraper.searchReddit(phrase, 50,60,5,10)

        for sentence in twitterResults:
            t1.insert(END, sentence.strip())
            t1.insert(END, "\n")
            #a procedure to reconfigure the size of Text widget
        height = t1.tk.call((t1._w, "count", "-update", "-displaylines", "1.0", "end"))
        t1.configure(height=height)
        master.update_idletasks()
        twitterStr = "Sentences from Twitter:    (" + twitterConf + "- " + f"{avgRT:.3f}" + " average retweets.)" 
        twitterbox.insert(END, twitterStr)
        
        for sentence in redditResults:
            t2.insert(END, sentence.strip())
            t2.insert(END,"\n")
            #a procedure to reconfigure the height of Text widget
        redditStr = "Sentences from Reddit:     (" + redditConf + "- " + f"{avgUV:.3f}" + " average upvotes.)"
        redditbox.insert(END, redditStr)
        height = t2.tk.call((t2._w, "count", "-update", "-displaylines", "1.0", "end"))
        t2.configure(height=height)
        master.update_idletasks()
        
        corpusResults, corpusConf = scraper.searchCorpus(phrase,10)
        for sentence in corpusResults:
            t3.insert(END, sentence)
            t3.insert(END,"\n")
            #a procedure to reconfigure the height of Text widget
        height = t3.tk.call((t3._w, "count", "-update", "-displaylines", "1.0", "end"))
        t3.configure(height=height)
        master.update_idletasks()
        corpusbox.insert(END, 'Sentences from books and news: ')
            
root = Tk()
my_gui = MyGUI(root)
root.mainloop()
