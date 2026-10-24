// Задание 4. Таблица умножения через функцию
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

func printTable(n int) {
	for i := 1; i <= 10; i++ {
		fmt.Printf("%d x %d = %d\n", n, i, n*i)
	}
}

func main() {
	for {
		n := readInt("Введите число от 1 до 10: ")

		if n < 1 || n > 10 {
			fmt.Println("Ошибка: число должно быть от 1 до 10")
			continue
		}

		printTable(n)

		fmt.Print("Повторить? (д/н): ")
		var answer string
		fmt.Scan(&answer)
		if answer != "д" {
			break
		}
		fmt.Println()
	}
}
