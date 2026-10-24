// Задание 3. Сумма и среднее от 1 до N
package main

import (
	"fmt"
	"os"
	"strconv"
)

func readInt(prompt string) int {
	for {
		fmt.Print(prompt)
		var s string
		if _, err := fmt.Scan(&s); err != nil {
			fmt.Println("Ошибка: не удалось прочитать ввод")
			os.Exit(1)
		}
		x, err := strconv.Atoi(s)
		if err != nil {
			fmt.Println("Ошибка: нужно ввести целое число")
			continue
		}
		return x
	}
}

func main() {
	for {
		n := readInt("Введите число N: ")

		if n <= 0 {
			fmt.Println("Ошибка: N должно быть больше нуля")
			continue
		}

		sum := 0
		for i := 1; i <= n; i++ {
			sum += i
		}

		fmt.Printf("Сумма чисел от 1 до %d: %d\n", n, sum)
		fmt.Printf("Среднее значение: %.2f\n", float64(sum)/float64(n))

		fmt.Print("Повторить? (д/н): ")
		var answer string
		fmt.Scan(&answer)
		if answer != "д" {
			break
		}
		fmt.Println()
	}
}
