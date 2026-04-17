SAMPLE DATA:

5673829777748902	AIRTEL	26070741334058715241	500
5857039905169608	AIRTEL	26070741334058715242	500
5579711759072144	AIRTEL	26070741334058715243	500
5079051519011519	AIRTEL	26070741334058715244	500
73964135796488741	MTN	00000036176194283	100
99358322908994021	MTN	00000036176194284	100
44741411249753611	MTN	00000036176194285	100
81909878243165631	MTN	00000036127070573	100
31782432928782506	MTN	00000036127070574	100
46985149948848407 MTN 500
87145490848136320 MTN 500

formats to:

AIRTEL ₦500
5673-8297-7774-8902 *311*PIN#
----------------
AIRTEL ₦500
5857-0399-0516-9608 *311*PIN#
----------------
AIRTEL ₦500
5579-7117-5907-2144 *311*PIN#
----------------
AIRTEL ₦500
5079-0515-1901-1519 *311*PIN#
----------------
MTN ₦100
7396-4135-7964-8874-1 *311*PIN#
----------------
MTN ₦100
9935-8322-9089-9402-1 *311*PIN#
----------------
MTN ₦100
4474-1411-2497-5361-1 *311*PIN#
----------------
MTN ₦100
8190-9878-2431-6563-1 *311*PIN#
----------------
MTN ₦100
3178-2432-9287-8250-6 *311*PIN#
----------------
MTN ₦500
4698-5149-9488-4840-7 *311*PIN#
----------------
MTN ₦500
8714-5490-8481-3632-0 *311*PIN#



You will build an EPIN Formatter that reads a text file that will contain the unformatted input data as shown above. Analyze the sample data very critically. Look at the input and output closely. There are only 4 possible networks: Airtel, MTN, GLO, and 9mobile. More could come later. In the input, The network name is usually what follows the EPIN regardless of the whitespaces between them. Remember that the network name comes after the EPIN so the EPIN should be on the left of the network name. The EPIN amount could be 100, 200 or 500. Nothing else for now but more amounts could come later. The EPIN amount usually comes after the network name and could be separated by whitespaces or other text or both, so you should be able to deduce the amount intuitively. Note that the EPIN digits are grouped in fours separated by dashes. Also, each EPIN set is separated by a line consisting of dashes. Allow the user to specify the number of dashes to be in that separator line. This can be an optional argument. Allow the user to optionally specially his company name, which will be displayed right before the network name of each EPIN set. Eg. DAMMIE OPTIMUS MTN ₦100. Note the last 2 input lines look kinda ideal.
