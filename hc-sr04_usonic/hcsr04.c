#include <stdio.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include "prussdrv.h"
#include "pruss_intc_mapping.h"

int mod(x)
{
	if (x >= 0)
		return x;
	else
		return (-1*x);
}

int main(void) {

	/* Initialize the PRU */
	printf(">> Initializing PRU\n");
	tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;
	prussdrv_init();

	/* Open PRU Interrupt */
	if (prussdrv_open (PRU_EVTOUT_0)) {
		// Handle failure
		fprintf(stderr, ">> PRU open failed\n");
		return 1;
	}

	/* Open PRU Interrupt */
	if (prussdrv_open (PRU_EVTOUT_1)) {
		// Handle failure
		fprintf(stderr, ">> PRU open failed\n");
		return 1;
	}


	/* Get the interrupt initialized */
	prussdrv_pruintc_init(&pruss_intc_initdata);

	/* Get pointers to PRU local memory */
	void *pruDataMem0, *pruDataMem1;
	prussdrv_map_prumem(PRUSS0_PRU0_DATARAM, &pruDataMem0);
	unsigned int *pruData0 = (unsigned int *) pruDataMem0;

	prussdrv_map_prumem(PRUSS0_PRU1_DATARAM, &pruDataMem1);
	unsigned int *pruData1 = (unsigned int *) pruDataMem1;

	/* Execute code on PRU */
	printf(">> Executing HCSR-04 code\n");
	prussdrv_exec_program(0, "hcsr04.bin");
	printf(">> Executing HCSR-04 code\n");
	prussdrv_exec_program(1, "hcsr04.bin");

	int a,b,prv_a,prv_b,flag=0,temp;
	/* Get measurements */
	FILE* fp;
	while (1) {


		prussdrv_pru_wait_event (PRU_EVTOUT_0);
		a = (int) pruData0[0] / 58.44;
		prussdrv_pru_clear_event(PRU_EVTOUT_0, PRU0_ARM_INTERRUPT);
		///////////////////////////this is for the second sensor///////////////////////////
		prussdrv_pru_wait_event (PRU_EVTOUT_0);
		b = (int) pruData0[0] / 58.44;
		prussdrv_pru_clear_event(PRU_EVTOUT_0, PRU0_ARM_INTERRUPT);	
		
		if(flag == 0)
		{
			prev_a = a;
			prev_b = b;
			flag = 1;
		}

		if( (mod(a-prv_a) > 10) && (mod(b-prv_b) > 10) )
		{
			temp = a;
			a = b;
			b = temp;
		}
		
		prv_a = a;
		prv_b = b;
			
		//Print the distance received from the sonar
		//At 20 degrees in dry air the speed of sound is 342.2 cm/sec
		//so it takes 29.12 us to make 1 cm, i.e. 58.44 us for a roundtrip of 1 cm
		fp = fopen("file.txt","w"); 
		printf("%d %d\n",a,b);
		fprintf(fp,"%d %d\n",a,b);
		fclose(fp);
	}
	// Disable PRU and close memory mapping
	prussdrv_pru_disable(0);
	prussdrv_exit();
	printf(">> PRU Disabled.\r\n");
	return (0);
}
